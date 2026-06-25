#!/usr/bin/env python3
"""
run_ingestion.py
Master ingestion runner — executes all steps in order.

Usage:
  python3 run_ingestion.py              # full run
  python3 run_ingestion.py --skip-seed  # skip Postgres seed, re-run Qdrant only
  python3 run_ingestion.py --test       # test connections only
"""
import sys, os, argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.dirname(__file__))

def test_connections():
    print("=== Testing Connections ===")
    # Postgres
    import psycopg2
    try:
        c = psycopg2.connect(host="localhost", port=5432, dbname="hci_os",
                             user="hci_admin", password="hci_postgres_2026")
        cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM projects")
        n = cur.fetchone()[0]
        c.close()
        print(f"  ✓ Postgres — {n} projects")
    except Exception as e:
        print(f"  ✗ Postgres: {e}")

    # Qdrant
    from qdrant_client import QdrantClient
    try:
        q = QdrantClient(host="localhost", port=6333)
        cols = q.get_collections().collections
        print(f"  ✓ Qdrant — {len(cols)} collections: {[c.name for c in cols]}")
    except Exception as e:
        print(f"  ✗ Qdrant: {e}")

    # Redis
    import redis
    try:
        r = redis.Redis(host="localhost", port=6379, password="hci_redis_2026")
        r.ping()
        print(f"  ✓ Redis — connected")
    except Exception as e:
        print(f"  ✗ Redis: {e}")

    # n8n
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:5678/healthz", timeout=3) as resp:
            print(f"  ✓ n8n — {resp.read().decode()}")
    except Exception as e:
        print(f"  ✗ n8n: {e}")

def main():
    parser = argparse.ArgumentParser(description="HCI AI Memory Ingestion Pipeline")
    parser.add_argument("--skip-seed",  action="store_true", help="Skip Postgres seeding")
    parser.add_argument("--test",       action="store_true", help="Test connections only")
    parser.add_argument("--collections-only", action="store_true", help="Create collections only")
    args = parser.parse_args()

    test_connections()

    if args.test:
        return

    print("\n=== Step 1: Create Qdrant Collections ===")
    from create_collections import create_all
    create_all()

    if args.collections_only:
        return

    if not args.skip_seed:
        print("\n=== Step 2: Seed Postgres ===")
        from seed_postgres import run as seed_run
        seed_run()
    else:
        print("\n=== Step 2: Skipping Postgres seed ===")

    print("\n=== Step 3: Ingest Memory into Qdrant ===")
    from ingest_memory import run as ingest_run
    ingest_run()

    print("\n" + "="*50)
    print("  HCI AI Memory Ingestion Complete")
    print("="*50)

    # Final counts
    from qdrant_client import QdrantClient
    q = QdrantClient(host="localhost", port=6333)
    for col in q.get_collections().collections:
        info = q.get_collection(col.name)
        print(f"  {col.name}: {info.points_count} vectors")

if __name__ == "__main__":
    main()
