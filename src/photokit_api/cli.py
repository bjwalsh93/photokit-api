"""CLI entry point for photokit-api.

Usage:
    photokit-api serve [--port 8787] [--host 127.0.0.1] [--no-auth] [--library PATH]
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="photokit-api",
        description="Local REST API for Apple Photos",
    )
    sub = parser.add_subparsers(dest="command")

    serve_p = sub.add_parser("serve", help="Start the API server")
    serve_p.add_argument("--port", type=int, default=8787)
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable bearer-token auth (not recommended)",
    )
    serve_p.add_argument(
        "--library",
        default=None,
        help="Path to Photos Library.photoslibrary (auto-detected if omitted)",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "serve":
        _serve(args)


def _serve(args: argparse.Namespace) -> None:
    import uvicorn

    from photokit_api import db
    from photokit_api.server.app import create_app
    from photokit_api.server.auth import get_or_create_token

    print(f"Loading Photos library...")
    db.get_db(library_path=args.library)
    print(f"Library loaded: {db.get_db().library_path}")

    use_auth = not args.no_auth
    if use_auth:
        token = get_or_create_token()
        print(f"Auth token: {token}")
        print(f"  Use: curl -H 'Authorization: Bearer {token}' http://{args.host}:{args.port}/stats")
    else:
        print("Auth DISABLED (--no-auth)")

    app = create_app(auth=use_auth)

    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"API docs: http://{args.host}:{args.port}/docs")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
