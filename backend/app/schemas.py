"""Pydantic schemas — ingestion validation + API response models.

The *In* schemas enforce the ingestion contract: records with missing required
fields or out-of-range values fail validation and are excluded from the unified
dataset (and therefore from ML inference). This is the Week-4 schema-validation
deliverable.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

STAGES = {
    "Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost",
}
HEALTH_BANDS = {"Healthy", "At-Risk", "Critical"}


# --------------------------------------------------------------------------- #
# Ingestion contracts (validated on the way into SQLite)
# --------------------------------------------------------------------------- #
class RepIn(BaseModel):
    rep_id: str
    name: str
    region: str
    segment: str
    tenure_months: int = Field(ge=0)
    quota: float = Field(ge=0)
    attainment_pct: float = Field(ge=0)
    historical_win_rate: float = Field(ge=0, le=1)
    activities_last_30d: int = Field(ge=0)
    avg_deal_cycle_days: int = Field(ge=0)


class AccountIn(BaseModel):
    account_id: str
    name: str
    industry: str
    region: str
    segment: str
    arr: float = Field(ge=0)
    engagement_score: float = Field(ge=0, le=1)
    support_tickets_30d: int = Field(ge=0)
    expansion_velocity: float
    avg_response_hours: int = Field(ge=0)
    days_to_renewal: int = Field(ge=0)
    health_band: str
    risk_score: float = Field(ge=0, le=1)

    @field_validator("health_band")
    @classmethod
    def _valid_band(cls, v: str) -> str:
        if v not in HEALTH_BANDS:
            raise ValueError(f"invalid health_band: {v!r}")
        return v


class DealIn(BaseModel):
    deal_id: str
    account_id: str
    rep_id: str
    stage: str
    amount: float = Field(gt=0)
    stage_weight: float = Field(ge=0, le=1)
    age_days: int = Field(ge=0)
    is_stalled: bool = False
    created_date: str
    expected_close_date: str
    probability_signal: float = Field(ge=0, le=1)
    won: int | None = None

    @field_validator("stage")
    @classmethod
    def _valid_stage(cls, v: str) -> str:
        if v not in STAGES:
            raise ValueError(f"invalid stage: {v!r}")
        return v


# --------------------------------------------------------------------------- #
# API response models
# --------------------------------------------------------------------------- #
class StageSummary(BaseModel):
    stage: str
    count: int
    total_amount: float
    weighted_amount: float
    ml_weighted_amount: float | None = None


class PipelineOverview(BaseModel):
    total_deals: int
    open_deals: int
    total_pipeline_value: float
    stage_weighted_forecast: float
    ml_forecast: float | None
    stages: list[StageSummary]


class DealOut(BaseModel):
    deal_id: str
    account_id: str
    rep_id: str
    stage: str
    amount: float
    age_days: int
    is_stalled: bool
    expected_close_date: str
    predicted_win_prob: float | None = None
    predicted_revenue: float | None = None


class AccountOut(BaseModel):
    account_id: str
    name: str
    industry: str
    segment: str
    arr: float
    engagement_score: float
    support_tickets_30d: int
    avg_response_hours: int
    days_to_renewal: int
    health_band: str
    risk_score: float


class AccountDetail(BaseModel):
    account: AccountOut
    deals: list[DealOut]
    open_pipeline_value: float
    weighted_pipeline_value: float


class RepOut(BaseModel):
    rep_id: str
    name: str
    region: str
    segment: str
    quota: float
    attainment_pct: float
    historical_win_rate: float
    activities_last_30d: int
    avg_deal_cycle_days: int



class IngestReport(BaseModel):
    domain: str
    received: int
    accepted: int
    rejected: int
    errors: list[str] = []


class IngestSummary(BaseModel):
    reports: list[IngestReport]
    total_accepted: int
    total_rejected: int


class ScenarioOut(BaseModel):
    available: list[str]
    planned_phase2: list[str] = []


class NarrativeOut(BaseModel):
    scenario: str
    source: str
    narrative: str
    brief: dict

