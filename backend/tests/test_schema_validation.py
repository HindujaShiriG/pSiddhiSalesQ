"""Week-4 QA: schema validation on ingestion."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import AccountIn, DealIn, RepIn


def _valid_deal() -> dict:
    return {
        "deal_id": "D1", "account_id": "A1", "rep_id": "R1",
        "stage": "Proposal", "amount": 50000, "stage_weight": 0.5,
        "age_days": 10, "is_stalled": False,
        "created_date": "2026-06-01", "expected_close_date": "2026-08-01",
        "probability_signal": 0.4, "won": None,
    }


def test_valid_deal_passes():
    deal = DealIn(**_valid_deal())
    assert deal.deal_id == "D1"


def test_missing_required_field_rejected():
    rec = _valid_deal()
    rec["amount"] = None
    with pytest.raises(ValidationError):
        DealIn(**rec)


def test_invalid_stage_rejected():
    rec = _valid_deal()
    rec["stage"] = "Bananas"
    with pytest.raises(ValidationError):
        DealIn(**rec)


def test_negative_amount_rejected():
    rec = _valid_deal()
    rec["amount"] = -10
    with pytest.raises(ValidationError):
        DealIn(**rec)


def test_win_rate_out_of_range_rejected():
    with pytest.raises(ValidationError):
        RepIn(
            rep_id="R1", name="X", region="North", segment="SMB",
            tenure_months=10, quota=1_000_000, attainment_pct=0.8,
            historical_win_rate=1.7, activities_last_30d=10, avg_deal_cycle_days=40,
        )


def test_invalid_health_band_rejected():
    with pytest.raises(ValidationError):
        AccountIn(
            account_id="A1", name="Acme", industry="SaaS", region="North", segment="SMB",
            arr=100000, engagement_score=0.5, support_tickets_30d=3, expansion_velocity=0.1,
            avg_response_hours=12, days_to_renewal=90, health_band="Excellent", risk_score=0.3,
        )
