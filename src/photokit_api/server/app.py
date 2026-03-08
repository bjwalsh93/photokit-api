"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from photokit_api.server.auth import TokenAuthMiddleware, get_or_create_token
from photokit_api.server.routes import albums, assets, images, stats


def create_app(*, auth: bool = True) -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="photokit-api",
        description="Local REST API for Apple Photos — read, search, serve, and delete.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if auth:
        token = get_or_create_token()
        app.add_middleware(TokenAuthMiddleware, token=token)

    app.include_router(assets.router)
    app.include_router(images.router)
    app.include_router(albums.router)
    app.include_router(stats.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    return app
