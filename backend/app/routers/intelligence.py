"""AI Sales Intelligence endpoints (Week 9 deliverable — Strong Quarter scenario)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai import narrative
from ..db import get_session

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.get("/scenarios")
def scenarios() -> dict:
    """Which scenarios are live now vs planned for Phase 2."""
    return {
        "available": list(narrative.PHASE1_SCENARIOS),
        "planned_phase2": [s for s in narrative.SCENARIOS if s not in narrative.PHASE1_SCENARIOS],
    }


@router.get("/narrative")
def get_narrative(
    scenario: str = "strong_quarter",
    session: Session = Depends(get_session),
) -> dict:
    try:
        return narrative.generate(session, scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
