"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with auth disabled."""
    from photokit_api.server.app import create_app

    app = create_app(auth=False)
    return TestClient(app)
