"""Rep performance data endpoints.

The Rep Performance *screen* is a Week-11 (Phase 2) deliverable, but the rep
domain is already integrated at mid-term, so this read endpoint is exposed now
for evidence and to unblock the frontend work.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..db import get_session

router = APIRouter(prefix="/api/reps", tags=["reps"])


@router.get("")
def list_reps(limit: int = 100, session: Session = Depends(get_session)) -> list[dict]:
    reps = (
        session.query(models.Rep)
        .order_by(models.Rep.historical_win_rate.desc())
        .limit(min(limit, 500))
        .all()
    )
    return [
        {
            "rep_id": r.rep_id,
            "name": r.name,
            "region": r.region,
            "segment": r.segment,
            "quota": r.quota,
            "attainment_pct": r.attainment_pct,
            "historical_win_rate": r.historical_win_rate,
            "activities_last_30d": r.activities_last_30d,
            "avg_deal_cycle_days": r.avg_deal_cycle_days,
        }
        for r in reps
    ]
