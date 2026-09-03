"""AI Sales Intelligence endpoints (Week 9 deliverable — Strong Quarter scenario)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai import narrative
from ..db import get_session
from ..schemas import NarrativeOut, ScenarioOut

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


@router.get("/scenarios", response_model=ScenarioOut)
def scenarios() -> ScenarioOut:
    """Which scenarios are available."""
    return ScenarioOut(
        available=list(narrative.AVAILABLE_SCENARIOS),
        planned_phase2=[],
    )


@router.get("/narrative", response_model=NarrativeOut)
def get_narrative(
    scenario: str = "strong_quarter",
    session: Session = Depends(get_session),
) -> NarrativeOut:
    try:
        data = narrative.generate(session, scenario)
        return NarrativeOut(**data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

