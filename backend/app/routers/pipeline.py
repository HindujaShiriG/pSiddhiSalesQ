"""Pipeline Overview screen endpoints (Week 7 deliverable)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..db import get_session
from ..schemas import DealOut, PipelineOverview, StageSummary

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

OPEN_STAGES = ("Prospecting", "Qualification", "Proposal", "Negotiation")


@router.get("/overview", response_model=PipelineOverview)
def overview(session: Session = Depends(get_session)) -> PipelineOverview:
    rows = (
        session.query(
            models.Deal.stage,
            func.count(models.Deal.deal_id),
            func.coalesce(func.sum(models.Deal.amount), 0.0),
            func.coalesce(func.sum(models.Deal.amount * models.Deal.stage_weight), 0.0),
            func.coalesce(func.sum(models.Deal.predicted_revenue), 0.0),
        )
        .group_by(models.Deal.stage)
        .all()
    )
    stages = [
        StageSummary(
            stage=stage,
            count=count,
            total_amount=round(total, 2),
            weighted_amount=round(weighted, 2),
            ml_weighted_amount=round(ml, 2),
        )
        for stage, count, total, weighted, ml in rows
    ]

    total_deals = session.query(func.count(models.Deal.deal_id)).scalar() or 0
    open_deals = session.query(func.count(models.Deal.deal_id)).filter(
        models.Deal.stage.in_(OPEN_STAGES)
    ).scalar() or 0
    total_value = session.query(func.coalesce(func.sum(models.Deal.amount), 0.0)).filter(
        models.Deal.stage.in_(OPEN_STAGES)
    ).scalar() or 0.0
    stage_forecast = session.query(
        func.coalesce(func.sum(models.Deal.amount * models.Deal.stage_weight), 0.0)
    ).filter(models.Deal.stage.in_(OPEN_STAGES)).scalar() or 0.0
    ml_forecast = session.query(
        func.coalesce(func.sum(models.Deal.predicted_revenue), 0.0)
    ).filter(models.Deal.stage.in_(OPEN_STAGES)).scalar() or 0.0

    return PipelineOverview(
        total_deals=total_deals,
        open_deals=open_deals,
        total_pipeline_value=round(total_value, 2),
        stage_weighted_forecast=round(stage_forecast, 2),
        ml_forecast=round(ml_forecast, 2) if ml_forecast else None,
        stages=sorted(stages, key=lambda s: s.stage),
    )


@router.get("/deals", response_model=list[DealOut])
def deals(
    stage: str | None = None,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[DealOut]:
    q = session.query(models.Deal)
    if stage:
        q = q.filter(models.Deal.stage == stage)
    q = q.order_by(models.Deal.predicted_revenue.desc().nullslast()).limit(min(limit, 500))
    return [DealOut.model_validate(d, from_attributes=True) for d in q.all()]
