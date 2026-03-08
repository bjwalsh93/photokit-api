"""Bearer token authentication middleware.

On first run, generates a random token and saves it to ~/.photokit-api/token.
Every request must include `Authorization: Bearer <token>`.
Disable with --no-auth on the CLI.
"""

from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

TOKEN_DIR = Path.home() / ".photokit-api"
TOKEN_FILE = TOKEN_DIR / "token"


def get_or_create_token() -> str:
    """Read existing token or generate a new one."""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)
    return token


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Reject requests without a valid bearer token."""

    def __init__(self, app, token: str) -> None:  # type: ignore[override]
        super().__init__(app)
        self.token = token

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.url.path in ("/docs", "/openapi.json", "/redoc", "/health"):
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {self.token}":
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization: Bearer <token>"},
            )
        return await call_next(request)
