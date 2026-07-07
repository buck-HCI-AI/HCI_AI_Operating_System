#!/usr/bin/env python3
"""
ingest_memory.py
Loads HCI data into Qdrant vector collections for semantic memory.
Uses fastembed (BAAI/bge-small-en-v1.5, 384 dims) — no API key required.

Collections populated:
  - vendor_memory:      all vendors with company + contact context
  - bid_memory:         all bid entries with project + package context
  - project_memory:     project summaries and status
  - constitution_memory: BOOK_00, AI_TEAM, SOPs as searchable docs
"""
import sys, os, glob, psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from fastembed import TextEmbedding
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ["POSTGRES_PASSWORD"],
)
Q      = QdrantClient(host="localhost", port=6333)
EMBED  = TextEmbedding("BAAI/bge-small-en-v1.5")

# ── helpers ───────────────────────────────────────────────────────────────────

def pg_rows(sql, params=None):
    c = psycopg2.connect(**DB)
    cur = c.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    cur.close(); c.close()
    return [dict(zip(cols, r)) for r in rows]

def upsert(collection, documents, metadatas, ids):
    """Embed documents with fastembed and upsert into Qdrant."""
    if not documents:
        return
    vectors = list(EMBED.embed(documents))
    points  = [
        PointStruct(id=ids[i], vector=list(vectors[i]), payload=metadatas[i])
        for i in range(len(documents))
    ]
    Q.upsert(collection_name=collection, points=points)

# ── vendor_memory ─────────────────────────────────────────────────────────────

def ingest_vendors():
    print("\n=== Ingesting vendor_memory ===")
    vendors = pg_rows("SELECT id, company_name, contact_name, email, phone, csi_divisions FROM vendors")
    if not vendors:
        print("  ✗ No vendors in Postgres — run seed_postgres.py first")
        return

    docs, metas, ids = [], [], []
    for v in vendors:
        csi = ", ".join(v["csi_divisions"]) if v["csi_divisions"] else "general"
        text = (
            f"Company: {v['company_name']}. "
            f"Contact: {v['contact_name'] or 'unknown'}. "
            f"CSI divisions: {csi}. "
            f"Email: {v['email'] or 'none'}. "
            f"Phone: {v['phone'] or 'none'}."
        )
        docs.append(text)
        metas.append({
            "vendor_id":    v["id"],
            "company_name": v["company_name"],
            "contact_name": v["contact_name"] or "",
            "csi_divisions": csi,
            "email":        v["email"] or "",
        })
        ids.append(v["id"])

    upsert("vendor_memory", docs, metas, ids)
    print(f"  ✓ {len(docs)} vendors ingested")

# ── bid_memory ────────────────────────────────────────────────────────────────

def ingest_bids():
    print("\n=== Ingesting bid_memory ===")
    bids = pg_rows("""
        SELECT be.id, be.bid_amount as amount, be.date_received as bid_date,
               be.status, be.notes,
               bp.package_name, bp.csi_division,
               p.name as project_name, p.address
        FROM bid_entries be
        JOIN bid_packages bp ON bp.id = be.bid_package_id
        JOIN projects p ON p.id = be.project_id
        ORDER BY be.id
    """)
    if not bids:
        print("  ✗ No bid entries in Postgres — run seed_postgres.py first")
        return

    docs, metas, ids = [], [], []
    for b in bids:
        amt_str = f"${b['amount']:,.0f}" if b['amount'] else "no amount recorded"
        text = (
            f"Bid for {b['package_name']} on {b['project_name']} ({b['address']}). "
            f"Amount: {amt_str}. "
            f"CSI: {b['csi_division'] or 'unspecified'}. "
            f"Status: {b['status'] or 'received'}. "
            f"Date received: {b['bid_date'] or 'unknown'}. "
            f"Notes: {b['notes'] or 'none'}."
        )
        docs.append(text)
        metas.append({
            "bid_id":       b["id"],
            "project_name": b["project_name"],
            "package_name": b["package_name"],
            "amount":       float(b["amount"]) if b["amount"] else 0,
            "status":       b["status"] or "",
            "csi_division": b["csi_division"] or "",
        })
        ids.append(b["id"])

    upsert("bid_memory", docs, metas, ids)
    print(f"  ✓ {len(docs)} bids ingested")

# ── project_memory ────────────────────────────────────────────────────────────

def ingest_projects():
    print("\n=== Ingesting project_memory ===")
    projects = pg_rows("SELECT id, name, address, city, state, status, scope FROM projects")

    docs, metas, ids = [], [], []
    for p in projects:
        text = (
            f"Project: {p['name']} at {p['address']}, {p['city']}, {p['state']}. "
            f"Scope: {p['scope'] or 'TBD'}. "
            f"Status: {p['status']}. "
            f"This is an active Hendrickson Construction high-end residential remodel."
        )
        docs.append(text)
        metas.append({
            "project_id":   p["id"],
            "project_name": p["name"],
            "address":      p["address"] or "",
            "scope":        p["scope"] or "",
            "status":       p["status"],
        })
        ids.append(p["id"])

    upsert("project_memory", docs, metas, ids)
    print(f"  ✓ {len(docs)} projects ingested")

# ── constitution_memory ───────────────────────────────────────────────────────

def ingest_constitution():
    print("\n=== Ingesting constitution_memory ===")

    doc_paths = [
        ("BOOK_00/README.md",                              "book00_readme"),
        ("BOOK_00/docs/AI_COLLABORATION_STANDARD_v1.md",   "ai_collab_standard"),
        ("BOOK_00/architecture/CURRENT_ARCHITECTURE.md",   "current_architecture"),
        ("BOOK_00/workflows/WORKFLOW_00_AI_COLLABORATION_LAYER.md", "workflow_00"),
        ("AI_TEAM/04_ARCHITECTURE.md",                     "architecture_detail"),
        ("AI_TEAM/03_DECISIONS.md",                        "decisions"),
        ("AI_TEAM/01_ROADMAP.md",                          "roadmap"),
        ("SESSION_STARTUP/QUICK_REFERENCE.md",             "quick_reference"),
        ("SESSION_STARTUP/SYSTEM_COMMANDS.md",             "system_commands"),
    ]

    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    docs, metas, ids = [], [], []

    for i, (rel_path, doc_id) in enumerate(doc_paths):
        full_path = os.path.join(repo, rel_path)
        if not os.path.exists(full_path):
            print(f"  - skip {rel_path} (not found)")
            continue
        with open(full_path) as f:
            content = f.read()
        # Chunk at ~800 chars to keep vectors focused
        chunks = [content[j:j+800] for j in range(0, len(content), 800)]
        for k, chunk in enumerate(chunks):
            docs.append(chunk)
            metas.append({
                "doc_id":   doc_id,
                "filename": rel_path,
                "chunk":    k,
                "title":    os.path.basename(rel_path),
            })
            ids.append(i * 100 + k + 1)
        print(f"  ✓ {rel_path} ({len(chunks)} chunks)")

    if docs:
        upsert("constitution_memory", docs, metas, ids)
        print(f"  ✓ {len(docs)} total chunks ingested")

# ── hci_procurement ───────────────────────────────────────────────────────────

def ingest_procurement():
    print("\n=== Ingesting hci_procurement ===")
    items = pg_rows("""
        SELECT pi.id, pi.item_name, pi.vendor, pi.po_number, pi.amount,
               pi.required_date, pi.status, p.name as project_name
        FROM procurement_items pi
        JOIN projects p ON p.id = pi.project_id
        ORDER BY pi.id
    """)
    if not items:
        print("  ✗ No procurement_items in Postgres")
        return

    docs, metas, ids = [], [], []
    for it in items:
        amt_str = f"${it['amount']:,.0f}" if it["amount"] else "no amount recorded"
        text = (
            f"Procurement item: {it['item_name']} for {it['project_name']}. "
            f"Vendor: {it['vendor'] or 'unassigned'}. PO number: {it['po_number'] or 'none'}. "
            f"Amount: {amt_str}. Required by: {it['required_date'] or 'unknown'}. "
            f"Status: {it['status']}."
        )
        docs.append(text)
        metas.append({
            "procurement_id": it["id"],
            "project_name":   it["project_name"],
            "item_name":      it["item_name"] or "",
            "vendor":         it["vendor"] or "",
            "amount":         float(it["amount"]) if it["amount"] else 0,
            "status":         it["status"] or "",
        })
        ids.append(it["id"])

    upsert("hci_procurement", docs, metas, ids)
    print(f"  ✓ {len(docs)} procurement items ingested")

# ── photo_memory ──────────────────────────────────────────────────────────────

def ingest_photos():
    print("\n=== Ingesting photo_memory ===")
    photos = pg_rows("""
        SELECT pa.id, pa.note, pa.findings, pa.safety_flags, pa.defect_flags,
               pa.progress_notes, pa.submitted_by, p.name as project_name
        FROM photo_analyses pa
        JOIN projects p ON p.id = pa.project_id
        ORDER BY pa.id
    """)
    if not photos:
        print("  ✗ No photo_analyses in Postgres")
        return

    docs, metas, ids = [], [], []
    for ph in photos:
        safety = ", ".join(ph["safety_flags"]) if ph["safety_flags"] else "none"
        defects = ", ".join(ph["defect_flags"]) if ph["defect_flags"] else "none"
        text = (
            f"Field photo from {ph['project_name']}, submitted by {ph['submitted_by']}. "
            f"Note: {ph['note'] or 'none'}. Findings: {ph['findings'] or 'none'}. "
            f"Safety flags: {safety}. Defect flags: {defects}. "
            f"Progress notes: {ph['progress_notes'] or 'none'}."
        )
        docs.append(text)
        metas.append({
            "photo_id":     ph["id"],
            "project_name": ph["project_name"],
            "submitted_by": ph["submitted_by"] or "",
            "safety_flags": safety,
            "defect_flags": defects,
        })
        ids.append(ph["id"])

    upsert("photo_memory", docs, metas, ids)
    print(f"  ✓ {len(docs)} photo analyses ingested")

# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    ingest_projects()
    ingest_vendors()
    ingest_bids()
    ingest_constitution()
    ingest_procurement()
    ingest_photos()
    print("\n  ✓ Memory ingestion complete")

if __name__ == "__main__":
    run()
