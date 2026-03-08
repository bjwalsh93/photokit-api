"""Album list and album-assets endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from photokit_api import db
from photokit_api.server.models import (
    AlbumListResponse,
    AssetListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/albums", tags=["albums"])


@router.get("", response_model=AlbumListResponse)
def list_albums() -> AlbumListResponse:
    albums = db.list_albums()
    return AlbumListResponse(albums=albums, total=len(albums))


@router.get(
    "/{uuid}/assets",
    response_model=AssetListResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_album_assets(
    uuid: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> AssetListResponse:
    assets, total = db.get_album_assets(uuid, limit=limit, offset=offset)
    if total == 0:
        raise HTTPException(status_code=404, detail=f"Album {uuid} not found or empty")
    return AssetListResponse(assets=assets, total=total, limit=limit, offset=offset)
