"""Shared Postgres + Qdrant + Redis connections."""
import os
import psycopg2
import psycopg2.extras
from qdrant_client import QdrantClient
import redis as redis_lib

DB_CONFIG = dict(
    host="localhost", port=5432,
    dbname="hci_os", user="hci_admin", password="hci_postgres_2026"
)

def pg():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.RealDictCursor)

Q = QdrantClient(host="localhost", port=6333)

REDIS = redis_lib.Redis(host="localhost", port=6379, password="hci_redis_2026", decode_responses=True)
