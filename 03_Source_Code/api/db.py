"""Shared Postgres + Qdrant + Redis connections."""
import os
import psycopg2
import psycopg2.extras
from qdrant_client import QdrantClient
import redis as redis_lib
from config import settings

DB_CONFIG = dict(
    host=settings.postgres_host,
    port=settings.postgres_port,
    dbname=settings.postgres_db,
    user=settings.postgres_user,
    password=settings.postgres_password,
)

def pg():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.RealDictCursor)

Q = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

REDIS = redis_lib.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True,
)
