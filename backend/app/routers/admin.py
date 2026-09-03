"""Admin/ops endpoints — trigger ingestion, training, and scoring.

In production these would be Azure Functions-style background triggers; for the
mid-term they are simple authenticated-by-obscurity POST endpoints used by the
CLI and the refresh button.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_session
from ..integration.ingest import ingest_all
from ..ml import predict, registry
from ..ml import train as trainer
from ..schemas import IngestSummary

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest", response_model=IngestSummary)
def run_ingest(session: Session = Depends(get_session)) -> IngestSummary:
    return ingest_all(session)


@router.post("/train")
def run_train(session: Session = Depends(get_session)) -> dict:
    try:
        return trainer.train_all(session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/score")
def run_score(session: Session = Depends(get_session)) -> dict:
    if not (registry.model_exists("win_scorer") and registry.model_exists("revenue_forecaster")):
        raise HTTPException(status_code=409, detail="models not trained — POST /api/admin/train first")
    deal_results = predict.score_open_deals(session)
    health_results = predict.predict_account_health(session)
    return {
        "deals": deal_results,
        "accounts": health_results,
    }


@router.get("/models")
def model_status() -> dict:
    out = {}
    for name in ("win_scorer", "revenue_forecaster", "health_classifier"):
        if registry.model_exists(name):
            _, meta = registry.load_model(name)
            out[name] = meta
        else:
            out[name] = {"status": "not_trained"}
    return out

