"""Database layer tests (require a real Photos library)."""

import pytest

from photokit_api import db


def test_get_db_returns_instance():
    photosdb = db.get_db()
    assert photosdb is not None
    assert hasattr(photosdb, "library_path")


def test_list_assets_returns_tuple():
    assets, total = db.list_assets(limit=5)
    assert isinstance(assets, list)
    assert isinstance(total, int)
    assert total >= 0


def test_get_stats_returns_model():
    stats = db.get_stats()
    assert stats.total_assets >= 0
    assert stats.total_photos >= 0


def test_list_albums():
    albums = db.list_albums()
    assert isinstance(albums, list)
