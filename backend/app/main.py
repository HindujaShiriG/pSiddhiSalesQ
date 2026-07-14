"""SalesIQ FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import accounts, admin, intelligence, pipeline, reps

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Unified Sales Operations System — Phase 1 (mid-term) API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router)
app.include_router(accounts.router)
app.include_router(reps.router)
app.include_router(intelligence.router)
app.include_router(admin.router)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}
