"""Route smoke tests.

These require a real Photos library to be meaningful; they verify
the API wiring and response shapes.
"""



def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_docs_accessible(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_stats_endpoint(client):
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_photos" in data
    assert "total_videos" in data


def test_assets_list(client):
    resp = client.get("/assets?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "assets" in data
    assert "total" in data
    assert data["limit"] == 5


def test_albums_list(client):
    resp = client.get("/albums")
    assert resp.status_code == 200
    data = resp.json()
    assert "albums" in data
    assert "total" in data


def test_asset_not_found(client):
    resp = client.get("/assets/nonexistent-uuid-12345")
    assert resp.status_code == 404
