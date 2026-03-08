"""Pydantic response models for the Photos API."""

from __future__ import annotations

from pydantic import BaseModel


class LocationModel(BaseModel):
    latitude: float
    longitude: float


class AssetModel(BaseModel):
    uuid: str
    filename: str
    original_filename: str | None = None
    date_created: str | None = None
    date_modified: str | None = None
    date_added: str | None = None
    media_type: str = "photo"
    width: int | None = None
    height: int | None = None
    file_size: int | None = None
    duration: float | None = None
    favorite: bool = False
    hidden: bool = False
    trashed: bool = False
    screenshot: bool = False
    has_adjustments: bool = False
    is_local: bool = True
    uti: str | None = None
    location: LocationModel | None = None
    keywords: list[str] = []
    albums: list[str] = []
    persons: list[str] = []
    labels: list[str] = []
    title: str | None = None
    description: str | None = None
    path: str | None = None
    path_edited: str | None = None


class AssetListResponse(BaseModel):
    assets: list[AssetModel]
    total: int
    limit: int
    offset: int


class AlbumModel(BaseModel):
    uuid: str
    title: str
    count: int
    creation_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    folder_names: list[str] = []


class AlbumListResponse(BaseModel):
    albums: list[AlbumModel]
    total: int


class StatsModel(BaseModel):
    total_photos: int
    total_videos: int
    total_assets: int
    total_albums: int
    favorites: int
    hidden: int
    trashed: int
    screenshots: int
    local: int
    cloud_only: int
    keywords: list[str] = []
    persons: list[str] = []


class BatchDeleteRequest(BaseModel):
    uuids: list[str]


class BatchDeleteResponse(BaseModel):
    success: bool
    deleted_count: int
    error: str | None = None


class ErrorResponse(BaseModel):
    detail: str
