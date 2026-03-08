"""PhotoKit bridge tests (macOS only, require Photos access)."""

import platform
import pytest

from photokit_api.photokit import DeleteResult, delete_assets


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_delete_empty_uuids():
    result = delete_assets([])
    assert isinstance(result, DeleteResult)
    assert result.success is False
    assert result.deleted_count == 0


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_delete_nonexistent_uuid():
    result = delete_assets(["00000000-0000-0000-0000-000000000000"])
    assert result.success is False
    assert result.deleted_count == 0
