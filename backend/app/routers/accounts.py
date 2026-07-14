"""Account Detail screen endpoints (Week 7 deliverable)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..db import get_session
from ..schemas import AccountDetail, AccountOut, DealOut

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

OPEN_STAGES = ("Prospecting", "Qualification", "Proposal", "Negotiation")


@router.get("", response_model=list[AccountOut])
def list_accounts(
    health_band: str | None = None,
    limit: int = 100,
    session: Session = Depends(get_session),
) -> list[AccountOut]:
    q = session.query(models.Account)
    if health_band:
        q = q.filter(models.Account.health_band == health_band)
    q = q.order_by(models.Account.risk_score.desc()).limit(min(limit, 500))
    return [AccountOut.model_validate(a, from_attributes=True) for a in q.all()]


@router.get("/{account_id}", response_model=AccountDetail)
def account_detail(account_id: str, session: Session = Depends(get_session)) -> AccountDetail:
    account = session.get(models.Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"account {account_id} not found")

    deals = (
        session.query(models.Deal)
        .filter(models.Deal.account_id == account_id)
        .order_by(models.Deal.predicted_revenue.desc().nullslast())
        .all()
    )
    open_value = sum(d.amount for d in deals if d.stage in OPEN_STAGES)
    weighted_value = sum(
        (d.predicted_revenue or d.amount * d.stage_weight) for d in deals if d.stage in OPEN_STAGES
    )

    return AccountDetail(
        account=AccountOut.model_validate(account, from_attributes=True),
        deals=[DealOut.model_validate(d, from_attributes=True) for d in deals],
        open_pipeline_value=round(open_value, 2),
        weighted_pipeline_value=round(weighted_value, 2),
    )
