# photokit-api launch posts

Copy-paste these. Took 2 min to write, will take you 5 min to post everywhere.

---

## Hacker News (Show HN)

**URL:** https://news.ycombinator.com/submit

**Title:**
```
Show HN: photokit-api – Local REST API for Apple Photos (Python/FastAPI)
```

**URL field:** `https://github.com/bjwalsh93/photokit-api`

**Text (leave blank if submitting a URL, or use this if doing a text post):**
```
I built a local REST API that exposes your entire Apple Photos library over HTTP. Search by date/album/person/keyword, serve originals/thumbnails/medium previews, and batch-delete — all from localhost.

Built with FastAPI + osxphotos for reads, pyobjc/PhotoKit for writes. Bearer token auth, localhost-only by default.

pip install photokit-api && photokit-api serve

I built this because I wanted to write apps against my photo library (like a Tinder-style photo tagger) without fighting AppleScript or Swift. Figured others might want the same thing.

Happy to answer questions about the osxphotos internals or the PhotoKit bridge.
```

---

## Reddit — r/python

**URL:** https://www.reddit.com/r/Python/submit

**Title:**
```
I built a local REST API for Apple Photos — search, serve images, and batch-delete from localhost
```

**Body:**
```
Hey r/python — I built photokit-api, a FastAPI server that turns your Apple Photos library into a REST API.

**What it does:**
- Search 10k+ photos by date, album, person, keyword, favorites, screenshots
- Serve originals, thumbnails (256px), and medium (1024px) previews
- Batch delete photos (one API call, one macOS dialog)
- Bearer token auth, localhost-only

**How:**
- Reads via osxphotos (fast SQLite access to Photos.sqlite)
- Image serving via FileResponse/sendfile
- Writes via pyobjc + PhotoKit (the only safe way to mutate Photos)

```
pip install photokit-api
photokit-api serve
# http://127.0.0.1:8787/docs
```

I built it because I wanted to write a photo tagger app without dealing with AppleScript or Swift. The whole thing is ~500 lines of Python.

GitHub: https://github.com/bjwalsh93/photokit-api

Feedback welcome — especially on what endpoints would be useful to add.
```

**Flair:** `I Made This`

---

## Reddit — r/selfhosted

**URL:** https://www.reddit.com/r/selfhosted/submit

**Title:**
```
photokit-api: Local REST API for Apple Photos — pip install and go
```

**Body:**
```
If you've ever wanted programmatic access to your Apple Photos library without iCloud APIs or a developer account, I built this.

photokit-api is a Python FastAPI server that runs locally and exposes your entire Photos library as a REST API. Search by any metadata, serve images at any resolution, batch delete.

- Localhost only, bearer token auth by default
- Reads from the Photos SQLite DB directly (fast)
- Writes go through Apple's PhotoKit (safe, respects iCloud sync)
- macOS only (that's where the Photos library lives)

Use case that motivated it: I built a Tinder-style swipe app to tag and clean up 12k+ photos. This API was the backend.

GitHub: https://github.com/bjwalsh93/photokit-api

`pip install photokit-api && photokit-api serve`
```

---

## Reddit — r/macapps

**URL:** https://www.reddit.com/r/macapps/submit

**Title:**
```
photokit-api — local REST API to search, serve, and manage your Apple Photos library
```

**Body:**
```
Built a local server that gives you a REST API over your Apple Photos library. Lets you search by date/album/person/keyword, download originals or thumbnails, and batch-delete — all from curl or any app.

Great if you want to build tools against your photo library without dealing with AppleScript or Swift.

GitHub: https://github.com/bjwalsh93/photokit-api

`pip install photokit-api && photokit-api serve` then hit http://127.0.0.1:8787/docs

macOS only, Python 3.9+, needs Full Disk Access for your terminal.
```

---

## Twitter / X

**Post 1 (main):**
```
I built a local REST API for Apple Photos.

pip install photokit-api
photokit-api serve

→ Search 12k photos by date, album, person, keyword
→ Serve originals, thumbs, medium previews
→ Batch delete with one API call
→ localhost only, token auth

All Python, ~500 lines. GitHub: https://github.com/bjwalsh93/photokit-api
```

**Post 2 (reply thread):**
```
Built this because I wanted a Tinder-style photo tagger — swipe through every photo, tag good/bad/neutral, bulk delete the junk.

Needed an API for my Photos library. There wasn't one. So I made one.

FastAPI + osxphotos for reads, pyobjc/PhotoKit for writes.
```

---

## Product Hunt

**URL:** https://www.producthunt.com/posts/new

**Tagline:**
```
Local REST API for your Apple Photos library
```

**Description:**
```
photokit-api turns your Apple Photos library into a searchable, programmable REST API running on localhost. Search by date, album, person, or keyword. Serve images at any resolution. Batch-delete junk photos. All from a simple pip install — no iCloud account, no Apple developer program, no Swift required. Built with Python, FastAPI, and osxphotos.
```

**Topics:** `Developer Tools`, `Photography`, `macOS`, `Open Source`, `API`

---

## PyPI publish

Run this in your terminal (you'll need a PyPI account + API token):

```bash
cd ~/Documents/photokit-api
source .venv/bin/activate
pip install build twine
python -m build
twine upload dist/*
# Enter your PyPI API token when prompted
```

Or set the token in your GitHub repo secrets as `PYPI_API_TOKEN`, create a GitHub release, and the publish workflow handles it automatically.
