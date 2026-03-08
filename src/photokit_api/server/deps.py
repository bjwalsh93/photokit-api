"""Shared dependencies injected into route handlers."""

from __future__ import annotations

from photokit_api import db as photosdb


def get_db() -> photosdb:
    """Return the db module (already holds the singleton PhotosDB)."""
    return photosdb
