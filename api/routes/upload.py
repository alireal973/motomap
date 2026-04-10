"""File upload API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List

from api.routes.auth import get_current_user
from api.services.storage import storage

router = APIRouter(prefix="/api/upload", tags=["upload"])


class UploadResponse:
    def __init__(self, url: str):
        self.url = url


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "general",
    user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    contents = await file.read()
    try:
        url = await storage.upload(
            file_bytes=contents,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=str(user.id),
            folder=folder,
        )
        return {"url": url}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    folder: str = "general",
    user=Depends(get_current_user),
):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files per upload")

    urls = []
    for f in files:
        if not f.filename:
            continue
        contents = await f.read()
        try:
            url = await storage.upload(
                file_bytes=contents,
                filename=f.filename,
                content_type=f.content_type or "application/octet-stream",
                user_id=str(user.id),
                folder=folder,
            )
            urls.append(url)
        except ValueError:
            continue

    return {"urls": urls, "count": len(urls)}
