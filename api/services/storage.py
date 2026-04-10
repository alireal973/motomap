"""File upload service with local + S3 support."""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
S3_BUCKET = os.getenv("S3_BUCKET", "")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class StorageService:
    def __init__(self):
        self._use_s3 = bool(S3_BUCKET)
        if not self._use_s3:
            Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    async def upload(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        folder: str = "general",
    ) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {ext}")
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Content type not allowed: {content_type}")
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)")

        file_hash = hashlib.md5(file_bytes).hexdigest()[:12]
        unique_name = f"{user_id}/{folder}/{file_hash}_{uuid.uuid4().hex[:8]}{ext}"

        if self._use_s3:
            return await self._upload_s3(file_bytes, unique_name, content_type)
        return await self._upload_local(file_bytes, unique_name)

    async def _upload_local(self, file_bytes: bytes, path: str) -> str:
        full_path = Path(UPLOAD_DIR) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_bytes)
        return f"/uploads/{path}"

    async def _upload_s3(self, file_bytes: bytes, key: str, content_type: str) -> str:
        try:
            import boto3
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=S3_BUCKET, Key=key, Body=file_bytes,
                ContentType=content_type, ACL="public-read",
            )
            region = s3.meta.region_name or "eu-central-1"
            return f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{key}"
        except ImportError:
            logger.warning("boto3 not installed, falling back to local storage")
            return await self._upload_local(file_bytes, key)

    async def delete(self, url: str) -> bool:
        if url.startswith("/uploads/"):
            path = Path(UPLOAD_DIR) / url.replace("/uploads/", "")
            if path.exists():
                path.unlink()
                return True
        elif self._use_s3 and S3_BUCKET in url:
            try:
                import boto3
                key = url.split(f"{S3_BUCKET}.s3.")[1].split("/", 1)[1] if ".s3." in url else ""
                if key:
                    s3 = boto3.client("s3")
                    s3.delete_object(Bucket=S3_BUCKET, Key=key)
                    return True
            except Exception as e:
                logger.warning("S3 delete failed: %s", e)
        return False


storage = StorageService()
