"""Shared Qdrant ingestion helper for workflow modules."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from fastembed import TextEmbedding

Q     = QdrantClient(host="localhost", port=6333)
_EMBED = None

def _embed():
    global _EMBED
    if _EMBED is None:
        _EMBED = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _EMBED

def upsert_one(collection: str, doc_id: int, text: str, payload: dict):
    """Embed a single text and upsert into Qdrant. Returns the point id."""
    vector = list(list(_embed().embed([text]))[0])
    Q.upsert(collection_name=collection, points=[
        PointStruct(id=doc_id, vector=vector, payload=payload)
    ])
    return doc_id
