"""PostgreSQL service — typed query helpers."""
import psycopg2, psycopg2.extras
from typing import List, Dict, Any, Optional
from config import settings


def connect():
    return psycopg2.connect(
        host=settings.postgres_host, port=settings.postgres_port,
        dbname=settings.postgres_db, user=settings.postgres_user,
        password=settings.postgres_password,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def query(sql: str, params=None) -> List[Dict[str, Any]]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def query_one(sql: str, params=None) -> Optional[Dict[str, Any]]:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=None) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


def execute_returning(sql: str, params=None) -> Optional[Dict[str, Any]]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
        conn.commit()
    return dict(row) if row else None


def table_exists(table_name: str) -> bool:
    row = query_one(
        "SELECT 1 FROM pg_tables WHERE tablename=%s AND schemaname='public'",
        (table_name,)
    )
    return row is not None
