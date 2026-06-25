"""MinIO object storage service."""
import io
from typing import List, Dict, Optional
from datetime import timedelta
from config import settings


def _client():
    from minio import Minio
    endpoint = settings.minio_endpoint.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )


def list_buckets() -> List[str]:
    return [b.name for b in _client().list_buckets()]


def list_objects(bucket: str, prefix: str = "", limit: int = 100) -> List[Dict]:
    objects = []
    for obj in _client().list_objects(bucket, prefix=prefix, recursive=True):
        objects.append({
            "key":           obj.object_name,
            "size":          obj.size,
            "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
            "etag":          obj.etag,
        })
        if len(objects) >= limit:
            break
    return objects


def put_object(bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    _client().put_object(bucket, key, io.BytesIO(data), length=len(data), content_type=content_type)
    return key


def get_presigned_url(bucket: str, key: str, expires_minutes: int = 60) -> str:
    return _client().presigned_get_object(bucket, key, expires=timedelta(minutes=expires_minutes))


def delete_object(bucket: str, key: str) -> None:
    _client().remove_object(bucket, key)


def object_exists(bucket: str, key: str) -> bool:
    try:
        _client().stat_object(bucket, key)
        return True
    except Exception:
        return False


def ping() -> bool:
    try:
        list_buckets()
        return True
    except Exception:
        return False
