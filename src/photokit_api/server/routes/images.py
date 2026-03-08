"""Image serving endpoints: original, thumbnail, medium."""

from __future__ import annotations

import io
import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from photokit_api import db

router = APIRouter(prefix="/assets", tags=["images"])

_THUMB_SIZE = 256
_MEDIUM_SIZE = 1024


def _guess_media_type(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


@router.get("/{uuid}/original", response_model=None)
def get_original(uuid: str) -> FileResponse:
    path = db.get_asset_path(uuid)
    if path is None or not Path(path).exists():
        raise HTTPException(status_code=404, detail="Original file not available (cloud-only?)")
    return FileResponse(path, media_type=_guess_media_type(path))


@router.get("/{uuid}/thumb", response_model=None)
def get_thumb(uuid: str):
    thumb_path = db.get_asset_thumb_path(uuid)
    if thumb_path and Path(thumb_path).exists():
        return FileResponse(thumb_path, media_type=_guess_media_type(thumb_path))
    original = db.get_asset_path(uuid)
    if original is None or not Path(original).exists():
        raise HTTPException(status_code=404, detail="No image available")
    return _resized_response(original, _THUMB_SIZE)


@router.get("/{uuid}/medium", response_model=None)
def get_medium(uuid: str):
    original = db.get_asset_path(uuid)
    if original is None or not Path(original).exists():
        raise HTTPException(status_code=404, detail="No image available")
    return _resized_response(original, _MEDIUM_SIZE)


def _resized_response(path: str, max_dim: int) -> StreamingResponse:
    from PIL import Image

    with Image.open(path) as img:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        fmt = "JPEG"
        if img.mode in ("RGBA", "LA", "P"):
            fmt = "PNG"
        img.save(buf, format=fmt, quality=85)
        buf.seek(0)

    media_type = "image/jpeg" if fmt == "JPEG" else "image/png"
    return StreamingResponse(buf, media_type=media_type)
