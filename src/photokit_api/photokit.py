"""PhotoKit write layer via pyobjc.

Provides delete_assets() which uses PHAssetChangeRequest.deleteAssets_()
inside performChangesAndWait_error_(). One call = one macOS confirmation dialog
for the entire batch.

Requires:
  - macOS
  - pyobjc-framework-Photos
  - Terminal/process must have Photos access in System Settings
"""

from __future__ import annotations

import logging
import platform
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeleteResult:
    success: bool
    deleted_count: int
    error: str | None = None


def _check_macos() -> None:
    if platform.system() != "Darwin":
        raise RuntimeError("PhotoKit operations require macOS")


def delete_assets(uuids: list[str]) -> DeleteResult:
    """Delete assets by UUID. Moves them to Recently Deleted in Photos.

    Triggers a single macOS confirmation dialog for the entire batch.
    Must be called from a background thread (not the main thread).
    """
    _check_macos()
    if not uuids:
        return DeleteResult(success=False, deleted_count=0, error="No UUIDs provided")

    try:
        import Photos  # pyobjc-framework-Photos
    except ImportError:
        return DeleteResult(
            success=False,
            deleted_count=0,
            error="pyobjc-framework-Photos not installed. Run: pip install pyobjc-framework-Photos",
        )

    local_ids = [f"{uuid}/L0/001" for uuid in uuids]
    fetch = Photos.PHAsset.fetchAssetsWithLocalIdentifiers_options_(local_ids, None)
    found_count = fetch.count()

    if found_count == 0:
        return DeleteResult(
            success=False,
            deleted_count=0,
            error=f"No matching assets found for {len(uuids)} UUID(s)",
        )

    logger.info("Requesting delete of %d assets (%d found)", len(uuids), found_count)

    def change_block():
        Photos.PHAssetChangeRequest.deleteAssets_(fetch)

    try:
        success, error = (
            Photos.PHPhotoLibrary.sharedPhotoLibrary().performChangesAndWait_error_(
                change_block, None
            )
        )
    except Exception as exc:
        return DeleteResult(success=False, deleted_count=0, error=str(exc))

    if success:
        logger.info("Successfully deleted %d assets", found_count)
        return DeleteResult(success=True, deleted_count=found_count)

    error_msg = "Unknown error"
    if error is not None and hasattr(error, "localizedDescription"):
        error_msg = str(error.localizedDescription())
        if "cancel" in error_msg.lower() or "3302" in error_msg:
            error_msg = "User cancelled the delete confirmation dialog"

    return DeleteResult(success=False, deleted_count=0, error=error_msg)


def set_favorite(uuid: str, is_favorite: bool) -> bool:
    """Set or unset the favorite flag on an asset. Returns True on success."""
    _check_macos()
    try:
        import Photos
    except ImportError:
        return False

    local_id = f"{uuid}/L0/001"
    fetch = Photos.PHAsset.fetchAssetsWithLocalIdentifiers_options_([local_id], None)
    if fetch.count() == 0:
        return False

    asset = fetch.objectAtIndex_(0)

    def change_block():
        req = Photos.PHAssetChangeRequest.changeRequestForAsset_(asset)
        req.setFavorite_(is_favorite)

    try:
        success, _ = (
            Photos.PHPhotoLibrary.sharedPhotoLibrary().performChangesAndWait_error_(
                change_block, None
            )
        )
        return bool(success)
    except Exception:
        return False
