"""
main.py  —  UniPay BNPL API entry point

Usage:
    python main.py
    python main.py --port 8080
    python main.py --host 0.0.0.0 --port 8000 --no-reload
"""
from __future__ import annotations

import argparse

import uvicorn
from fastapi import FastAPI

from app.api import register_exception_handlers
from app.api.v1 import router as v1_router
from app.database import engine
from app.models.base import Base


def create_app() -> FastAPI:
    app = FastAPI(
        title="UniPay BNPL API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(v1_router)
    register_exception_handlers(app)

    return app


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="UniPay BNPL API server")
    p.add_argument("--host", default="127.0.0.1", help="Bind host")
    p.add_argument("--port", default=8000, type=int, help="Bind port")
    p.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    return p.parse_args()


app = create_app()


if __name__ == "__main__":
    args = _parse()
    print(f"\n  💳  UniPay BNPL API")
    print(f"  ➜   http://{args.host}:{args.port}/docs\n")
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
    )