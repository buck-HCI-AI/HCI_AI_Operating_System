#!/usr/bin/env python3
"""
create_collections.py
Creates all 7 Qdrant collections for HCI AI memory.
Safe to re-run — skips collections that already exist.

Vector model: BAAI/bge-small-en-v1.5 via fastembed (384 dims, cosine)
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
VECTOR_SIZE = 384
DISTANCE    = Distance.COSINE

COLLECTIONS = {
    "project_memory": "Project events, decisions, issues, outcomes per project",
    "vendor_memory":  "Vendor interactions, bid history, performance, relationships",
    "meeting_memory": "Meeting summaries, transcripts, action items",
    "lessons_learned":"Failures, successes, warnings, recommendations across projects",
    "bid_memory":     "Bid history, amounts, market intelligence per CSI division",
    "constitution_memory": "SOPs, standards, HCI AI constitution, engineering docs",
    "photo_memory":   "Jobsite photos with AI-extracted descriptions (future)",
}

def create_all():
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    existing = {c.name for c in client.get_collections().collections}

    for name, description in COLLECTIONS.items():
        if name in existing:
            print(f"  ✓ {name} — already exists")
            continue
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
        )
        print(f"  + {name} — created ({description[:50]}...)")

    final = {c.name for c in client.get_collections().collections}
    print(f"\n  {len(final)} collections live: {', '.join(sorted(final))}")

if __name__ == "__main__":
    print("=== Creating Qdrant Collections ===")
    create_all()
