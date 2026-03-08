"""Asset list, detail, and delete endpoints."""

from __future__ import annotations

import asyncio
import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from photokit_api import db
from photokit_api.photokit import delete_assets as pk_delete
from photokit_api.server.models import (
    AssetListResponse,
    AssetModel,
    BatchDeleteRequest,
    BatchDeleteResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
def list_assets(
    type: Optional[str] = Query(None, description="photo or video"),
    favorite: Optional[bool] = Query(None),
    hidden: Optional[bool] = Query(None),
    trashed: Optional[bool] = Query(None),
    screenshot: Optional[bool] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date, e.g. 2024-01-01"),
    date_to: Optional[str] = Query(None, description="ISO date, e.g. 2024-12-31"),
    album: Optional[str] = Query(None, description="Album name"),
    keyword: Optional[str] = Query(None),
    person: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> AssetListResponse:
    dt_from = None
    dt_to = None
    if date_from:
        dt_from = datetime.datetime.fromisoformat(date_from)
    if date_to:
        dt_to = datetime.datetime.fromisoformat(date_to)

    assets, total = db.list_assets(
        media_type=type,
        favorite=favorite,
        hidden=hidden,
        trashed=trashed,
        screenshot=screenshot,
        date_from=dt_from,
        date_to=dt_to,
        album=album,
        keyword=keyword,
        person=person,
        limit=limit,
        offset=offset,
    )
    return AssetListResponse(assets=assets, total=total, limit=limit, offset=offset)


@router.get(
    "/{uuid}",
    response_model=AssetModel,
    responses={404: {"model": ErrorResponse}},
)
def get_asset(uuid: str) -> AssetModel:
    asset = db.get_asset(uuid)
    if asset is None:
        raise HTTPException(status_code=404, detail=f"Asset {uuid} not found")
    return asset


@router.delete("/batch", response_model=BatchDeleteResponse)
async def batch_delete(body: BatchDeleteRequest) -> BatchDeleteResponse:
    """Batch delete assets by UUID.

    Moves them to Recently Deleted in Photos. Triggers a single macOS
    confirmation dialog for the entire batch — click OK once.
    """
    if not body.uuids:
        raise HTTPException(status_code=400, detail="No UUIDs provided")
    if len(body.uuids) > 5000:
        raise HTTPException(status_code=400, detail="Max 5000 UUIDs per batch")

    result = await asyncio.to_thread(pk_delete, body.uuids)
    return BatchDeleteResponse(
        success=result.success,
        deleted_count=result.deleted_count,
        error=result.error,
    )
