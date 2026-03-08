"""Library stats endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from photokit_api import db
from photokit_api.server.models import StatsModel

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsModel)
def get_stats() -> StatsModel:
    return db.get_stats()


@router.post("/reload", response_model=dict)
def reload_library() -> dict:
    """Force-reload the Photos database to pick up changes."""
    db.reload_db()
    return {"status": "reloaded"}
