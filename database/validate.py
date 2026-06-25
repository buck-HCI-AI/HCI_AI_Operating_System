#!/usr/bin/env python3
"""
HCI AI — Data Architecture Validation
Runs 10 checks per the directive. Run before building higher-level services.

Usage:
    python3 database/validate.py
"""
import sys, os, json, uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03_Source_Code", "integrations"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

PASS = "  ✓"
FAIL = "  ✗"
results = []

def check(name, fn):
    try:
        fn()
        print(f"{PASS} {name}")
        results.append((name, True, None))
    except Exception as e:
        print(f"{FAIL} {name}: {e}")
        results.append((name, False, str(e)))

print("\n=== HCI AI Data Architecture Validation ===\n")

# 1. PostgreSQL accepts connections
def chk_postgres():
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", "hci_postgres_2026"),
    )
    conn.close()
check("PostgreSQL connection", chk_postgres)

# 2. Redis responds to PING
def chk_redis():
    import redis
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        password=os.environ.get("REDIS_PASSWORD", "hci_redis_2026"),
    )
    assert r.ping() == True
check("Redis PING", chk_redis)

# 3. Qdrant responds
def chk_qdrant():
    import ssl, certifi, urllib.request
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(f"http://{os.environ.get('QDRANT_HOST','localhost')}:{os.environ.get('QDRANT_PORT',6333)}/")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())
    assert "title" in data or "version" in data or r.status == 200
check("Qdrant connection", chk_qdrant)

# 4. Core tables exist
def chk_tables():
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST","localhost"), port=5432,
        dbname=os.environ.get("POSTGRES_DB","hci_os"),
        user=os.environ.get("POSTGRES_USER","hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD","hci_postgres_2026"),
    )
    cur = conn.cursor()
    required = ["projects", "vendors", "bid_packages", "bid_entries", "lessons_learned",
                "meetings", "daily_logs", "hubspot_deals", "drive_sync_log"]
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    existing = {r[0] for r in cur.fetchall()}
    missing = [t for t in required if t not in existing]
    conn.close()
    if missing:
        raise Exception(f"Missing tables: {missing}")
    return f"{len(existing)} tables found"
check("Core schema tables exist", chk_tables)

# 5. Projects seeded
def chk_projects():
    import psycopg2
    conn = psycopg2.connect(
        host="localhost", port=5432, dbname="hci_os",
        user="hci_admin", password=os.environ.get("POSTGRES_PASSWORD","hci_postgres_2026"),
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0]
    conn.close()
    assert count >= 3, f"Expected 3+ projects, found {count}"
check("Seed data: projects loaded", chk_projects)

# 6. Drive sync log has data
def chk_drive_sync():
    import psycopg2
    conn = psycopg2.connect(
        host="localhost", port=5432, dbname="hci_os",
        user="hci_admin", password=os.environ.get("POSTGRES_PASSWORD","hci_postgres_2026"),
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM drive_sync_log")
    count = cur.fetchone()[0]
    conn.close()
    assert count > 0, "drive_sync_log is empty — run sync_drive.py first"
check("Drive sync log has entries", chk_drive_sync)

# 7. Qdrant drive_memory collection exists and has vectors
def chk_qdrant_vectors():
    from qdrant_client import QdrantClient
    client = QdrantClient(
        host=os.environ.get("QDRANT_HOST", "localhost"),
        port=int(os.environ.get("QDRANT_PORT", 6333))
    )
    info = client.get_collection("drive_memory")
    assert info.points_count > 0, f"drive_memory has 0 vectors"
check("Qdrant: drive_memory vectors exist", chk_qdrant_vectors)

# 8. Sample document metadata insert (with rollback)
def chk_doc_insert():
    import psycopg2
    conn = psycopg2.connect(
        host="localhost", port=5432, dbname="hci_os",
        user="hci_admin", password=os.environ.get("POSTGRES_PASSWORD","hci_postgres_2026"),
    )
    cur = conn.cursor()
    test_id = str(uuid.uuid4())
    try:
        cur.execute("SELECT id FROM projects LIMIT 1")
        proj = cur.fetchone()
        proj_id = proj[0] if proj else None
        # Insert into existing legacy documents-style table check
        cur.execute("SELECT 1 FROM pg_tables WHERE tablename='documents' AND schemaname='public'")
        has_docs = cur.fetchone()
        if not has_docs:
            raise Exception("documents table not yet created (new schema not applied)")
        cur.execute("""
            INSERT INTO documents (title, document_category, original_filename,
                normalized_filename, checksum_sha256, storage_bucket, storage_object_key,
                source_system, project_id)
            VALUES ('Validation Test Doc', 'unknown', 'test.pdf', 'validate/test.pdf',
                %s, 'hci-raw-documents', 'validate/test.pdf', 'validation', %s)
            RETURNING id
        """, (test_id[:64], proj_id))
        new_id = cur.fetchone()[0]
        conn.rollback()  # don't save test data
    finally:
        conn.close()
check("Sample document row insert (rolled back)", chk_doc_insert)

# 9. MinIO reachable (not necessarily running yet)
def chk_minio():
    import urllib.request
    try:
        endpoint = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
        req = urllib.request.Request(f"{endpoint}/minio/health/live")
        with urllib.request.urlopen(req, timeout=5) as r:
            assert r.status == 200
    except Exception:
        raise Exception("MinIO not running — start with: cd infrastructure && docker compose up -d minio minio-init")
check("MinIO health check", chk_minio)

# 10. Schema SQL files exist in repo
def chk_schema_files():
    base = os.path.join(os.path.dirname(__file__), "schema")
    required = ["001_initial_core_schema.sql", "002_document_storage_schema.sql",
                "003_registry_schema.sql", "004_embedding_metadata_schema.sql"]
    missing = [f for f in required if not os.path.exists(os.path.join(base, f))]
    if missing:
        raise Exception(f"Missing schema files: {missing}")
check("Schema SQL files present in repo", chk_schema_files)

# Summary
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n{'='*44}")
print(f"  {passed}/{total} checks passed")
if passed == total:
    print("  Foundation is ready for higher-level services.")
else:
    print("  Fix failures before building on top.")
print(f"{'='*44}\n")
sys.exit(0 if passed == total else 1)
