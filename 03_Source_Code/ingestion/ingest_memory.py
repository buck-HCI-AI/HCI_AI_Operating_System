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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DB     = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")
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

# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    ingest_projects()
    ingest_vendors()
    ingest_bids()
    ingest_constitution()
    print("\n  ✓ Memory ingestion complete")

if __name__ == "__main__":
    run()
