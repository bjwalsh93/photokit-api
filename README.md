# photokit-api

[![PyPI version](https://img.shields.io/pypi/v/photokit-api.svg)](https://pypi.org/project/photokit-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Python](https://img.shields.io/pypi/pyversions/photokit-api.svg)](https://pypi.org/project/photokit-api/)

**Local REST API for Apple Photos** — read, search, serve images, and batch-delete, all from `localhost`.

```
pip install photokit-api
photokit-api serve
```

Then hit `http://127.0.0.1:8787/docs` for the interactive API explorer.

---

## Why

Apple Photos has no API. You can't programmatically search your library, serve thumbnails, or delete junk photos without fighting AppleScript, PhotoKit, and an undocumented SQLite database.

**photokit-api** wraps all of that into a clean REST API:

- **Read** metadata for 12,000+ photos in milliseconds (direct SQLite via [osxphotos](https://github.com/RhetTbull/osxphotos))
- **Serve** originals, thumbnails, and medium-res previews via `sendfile()` (~1ms)
- **Delete** photos in batch — one API call, one macOS confirmation dialog (via PhotoKit + pyobjc)
- **Search** by date, album, keyword, person, favorite, screenshot, media type
- **Secure** by default — bearer token auth, localhost-only binding

## Quick Start

### 1. Install

```bash
pip install photokit-api
```

Requires **macOS** and **Python 3.10+**. Your terminal needs **Full Disk Access** (System Settings > Privacy & Security > Full Disk Access).

### 2. Start the server

```bash
photokit-api serve
```

On first run it:
- Loads your Photos library (auto-detected)
- Generates an auth token at `~/.photokit-api/token`
- Starts the API on `http://127.0.0.1:8787`

### 3. Use it

```bash
# The token is printed on startup, or read it from ~/.photokit-api/token
TOKEN=$(cat ~/.photokit-api/token)

# Library stats
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/stats

# List recent photos
curl -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8787/assets?limit=10"

# Get a specific photo
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/assets/SOME-UUID-HERE

# Download original
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/assets/SOME-UUID/original -o photo.jpg

# Get 256px thumbnail
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/assets/SOME-UUID/thumb -o thumb.jpg

# Search screenshots
curl -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8787/assets?screenshot=true&limit=50"

# Search by date range
curl -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8787/assets?date_from=2024-01-01&date_to=2024-06-30"

# List albums
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/albums

# Batch delete (moves to Recently Deleted — one confirmation dialog)
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"uuids": ["UUID-1", "UUID-2", "UUID-3"]}' \
  http://127.0.0.1:8787/assets/batch
```

## API Reference

### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/assets` | List/search assets |
| `GET` | `/assets/{uuid}` | Get single asset metadata |
| `GET` | `/assets/{uuid}/original` | Stream original file |
| `GET` | `/assets/{uuid}/thumb` | 256px thumbnail |
| `GET` | `/assets/{uuid}/medium` | 1024px preview |
| `DELETE` | `/assets/batch` | Batch delete by UUIDs |

#### `GET /assets` Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `type` | `photo` / `video` | Filter by media type |
| `favorite` | `bool` | Filter by favorite status |
| `hidden` | `bool` | Filter by hidden status |
| `trashed` | `bool` | Filter by trashed status |
| `screenshot` | `bool` | Filter screenshots |
| `date_from` | ISO date | Start of date range |
| `date_to` | ISO date | End of date range |
| `album` | `string` | Filter by album name |
| `keyword` | `string` | Filter by keyword |
| `person` | `string` | Filter by person name |
| `limit` | `int` | Page size (1-1000, default 100) |
| `offset` | `int` | Page offset (default 0) |

### Albums

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/albums` | List all albums |
| `GET` | `/albums/{uuid}/assets` | Assets in a specific album |

### Stats & Meta

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stats` | Library summary (counts, keywords, persons) |
| `POST` | `/reload` | Force-reload the Photos database |
| `GET` | `/health` | Health check (no auth required) |
| `GET` | `/docs` | Interactive API docs (no auth required) |

## CLI Options

```bash
photokit-api serve [OPTIONS]

Options:
  --port INT       Port to bind (default: 8787)
  --host TEXT      Host to bind (default: 127.0.0.1)
  --no-auth        Disable bearer token auth
  --library PATH   Path to Photos Library (auto-detected if omitted)
```

## Architecture

```
Read path:   FastAPI → osxphotos → Photos.sqlite (read-only)
Image path:  FastAPI → FileResponse → originals/ on disk (sendfile)
Write path:  FastAPI → pyobjc → PhotoKit → PHAssetChangeRequest
```

- **Reads** go through [osxphotos](https://github.com/RhetTbull/osxphotos), which handles the Photos.sqlite schema across macOS versions. No direct SQL needed.
- **Images** are served directly from disk using `FileResponse` (kernel-level `sendfile()`). Thumbnails fall back to Pillow resize if no derivative exists.
- **Writes** (delete, favorite) use Apple's PhotoKit framework via [pyobjc](https://pyobjc.readthedocs.io/). This is the only safe way to mutate the Photos library — it goes through Apple's own APIs and respects iCloud sync.

## Security

- Server binds to `127.0.0.1` only (never `0.0.0.0`)
- Bearer token auto-generated on first run, saved to `~/.photokit-api/token`
- API docs (`/docs`) and health check (`/health`) are accessible without auth
- CORS restricted to localhost origins

## Requirements

- **macOS** (Catalina or later)
- **Python 3.10+**
- **Full Disk Access** for your terminal app (System Settings > Privacy & Security)
- **Photos access** for your terminal app (System Settings > Privacy & Security > Photos)

## Development

```bash
git clone https://github.com/photokit-api/photokit-api.git
cd photokit-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
