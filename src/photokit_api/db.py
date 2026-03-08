"""Photos database read layer using osxphotos.

Wraps osxphotos.PhotosDB as a singleton. All reads go through here —
never touch Photos.sqlite directly from routes.
"""

from __future__ import annotations

import datetime
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import osxphotos
from osxphotos import PhotosDB, QueryOptions

from photokit_api.server.models import (
    AlbumModel,
    AssetModel,
    LocationModel,
    StatsModel,
)

logger = logging.getLogger(__name__)

_db: PhotosDB | None = None


def get_db(library_path: str | None = None) -> PhotosDB:
    """Return a cached PhotosDB instance (singleton)."""
    global _db
    if _db is None:
        if library_path:
            _db = PhotosDB(library_path)
        else:
            _db = PhotosDB()
        logger.info("PhotosDB loaded: %s", _db.library_path)
    return _db


def reload_db(library_path: str | None = None) -> PhotosDB:
    """Force-reload the database (picks up new photos from iCloud sync, etc.)."""
    global _db
    _db = None
    return get_db(library_path)


def _photo_to_asset(photo: Any) -> AssetModel:
    """Convert an osxphotos PhotoInfo to our AssetModel."""
    loc = None
    if photo.location and photo.location[0] is not None:
        loc = LocationModel(latitude=photo.location[0], longitude=photo.location[1])

    media_type = "photo" if photo.isphoto else "video"

    return AssetModel(
        uuid=photo.uuid,
        filename=photo.filename or "",
        original_filename=photo.original_filename,
        date_created=photo.date.isoformat() if photo.date else None,
        date_modified=photo.date_modified.isoformat() if photo.date_modified else None,
        date_added=photo.date_added.isoformat() if photo.date_added else None,
        media_type=media_type,
        width=getattr(photo, "width", None),
        height=getattr(photo, "height", None),
        file_size=getattr(photo, "original_filesize", None),
        duration=getattr(photo, "duration", None),
        favorite=photo.favorite,
        hidden=photo.hidden,
        trashed=getattr(photo, "intrash", False),
        screenshot=photo.screenshot,
        has_adjustments=photo.hasadjustments,
        is_local=photo.path is not None,
        uti=getattr(photo, "uti", None),
        location=loc,
        keywords=list(photo.keywords) if photo.keywords else [],
        albums=list(photo.albums) if photo.albums else [],
        persons=list(photo.persons) if photo.persons else [],
        labels=list(photo.labels) if photo.labels else [],
        title=photo.title,
        description=photo.description or None,
        path=photo.path,
        path_edited=photo.path_edited,
    )


def list_assets(
    *,
    media_type: str | None = None,
    favorite: bool | None = None,
    hidden: bool | None = None,
    trashed: bool | None = None,
    screenshot: bool | None = None,
    date_from: datetime.datetime | None = None,
    date_to: datetime.datetime | None = None,
    album: str | None = None,
    keyword: str | None = None,
    person: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AssetModel], int]:
    """List/search assets with filters. Returns (page, total_count)."""
    db = get_db()
    opts = QueryOptions(
        photos=media_type in (None, "photo"),
        movies=media_type in (None, "video"),
        favorite=favorite if favorite is True else None,
        hidden=hidden if hidden is True else None,
        screenshot=screenshot if screenshot is True else None,
        from_date=date_from,
        to_date=date_to,
        album=([album] if album else None),
        keyword=([keyword] if keyword else None),
        person=([person] if person else None),
    )
    photos = db.query(opts)

    if favorite is False:
        photos = [p for p in photos if not p.favorite]
    if hidden is False:
        photos = [p for p in photos if not p.hidden]
    if trashed is True:
        photos = [p for p in photos if getattr(p, "intrash", False)]
    elif trashed is False:
        photos = [p for p in photos if not getattr(p, "intrash", False)]

    photos.sort(key=lambda p: (p.date or datetime.datetime.min), reverse=True)
    total = len(photos)
    page = [_photo_to_asset(p) for p in photos[offset : offset + limit]]
    return page, total


def get_asset(uuid: str) -> AssetModel | None:
    """Get a single asset by UUID."""
    db = get_db()
    photo = db.get_photo(uuid)
    if photo is None:
        return None
    return _photo_to_asset(photo)


def get_asset_path(uuid: str) -> str | None:
    """Get the on-disk path for an asset's original file."""
    db = get_db()
    photo = db.get_photo(uuid)
    if photo is None:
        return None
    return photo.path


def get_asset_thumb_path(uuid: str) -> str | None:
    """Get a thumbnail/derivative path for an asset."""
    db = get_db()
    photo = db.get_photo(uuid)
    if photo is None:
        return None
    derivs = getattr(photo, "path_derivatives", None)
    if derivs:
        return derivs[-1] if isinstance(derivs, list) else derivs
    return photo.path


def list_albums() -> list[AlbumModel]:
    """List all user albums."""
    db = get_db()
    albums = []
    for a in db.album_info:
        albums.append(
            AlbumModel(
                uuid=a.uuid,
                title=a.title,
                count=len(a.photos),
                creation_date=(
                    a.creation_date.isoformat() if getattr(a, "creation_date", None) else None
                ),
                start_date=(
                    a.start_date.isoformat() if getattr(a, "start_date", None) else None
                ),
                end_date=a.end_date.isoformat() if getattr(a, "end_date", None) else None,
                folder_names=list(a.folder_names) if getattr(a, "folder_names", None) else [],
            )
        )
    return albums


def get_album_assets(album_uuid: str, limit: int = 100, offset: int = 0) -> tuple[list[AssetModel], int]:
    """Get assets belonging to a specific album."""
    db = get_db()
    for a in db.album_info:
        if a.uuid == album_uuid:
            photos = a.photos
            total = len(photos)
            page = [_photo_to_asset(p) for p in photos[offset : offset + limit]]
            return page, total
    return [], 0


def get_stats() -> StatsModel:
    """Get library summary statistics."""
    db = get_db()
    all_photos = db.photos(images=True, movies=False)
    all_videos = db.photos(images=False, movies=True)
    all_assets = all_photos + all_videos

    return StatsModel(
        total_photos=len(all_photos),
        total_videos=len(all_videos),
        total_assets=len(all_assets),
        total_albums=len(db.album_info),
        favorites=sum(1 for p in all_assets if p.favorite),
        hidden=sum(1 for p in all_assets if p.hidden),
        trashed=len(db.photos(intrash=True)),
        screenshots=sum(1 for p in all_assets if p.screenshot),
        local=sum(1 for p in all_assets if p.path is not None),
        cloud_only=sum(1 for p in all_assets if p.path is None),
        keywords=list(db.keywords) if db.keywords else [],
        persons=list(db.persons) if db.persons else [],
    )
