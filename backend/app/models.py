"""SQLAlchemy ORM models — the normalised unified dataset (3 CRM domains).

Indexes are declared on hot columns (foreign keys, stage, health band) so the
portal renders fast — pre-empting Risk #4 in the approved proposal.
"""
from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Rep(Base):
    __tablename__ = "reps"

    rep_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String)
    segment: Mapped[str] = mapped_column(String)
    tenure_months: Mapped[int] = mapped_column(Integer)
    quota: Mapped[float] = mapped_column(Float)
    attainment_pct: Mapped[float] = mapped_column(Float)
    historical_win_rate: Mapped[float] = mapped_column(Float)
    activities_last_30d: Mapped[int] = mapped_column(Integer)
    avg_deal_cycle_days: Mapped[int] = mapped_column(Integer)

    deals: Mapped[list["Deal"]] = relationship(back_populates="rep")


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String)
    segment: Mapped[str] = mapped_column(String)
    arr: Mapped[float] = mapped_column(Float)
    engagement_score: Mapped[float] = mapped_column(Float)
    support_tickets_30d: Mapped[int] = mapped_column(Integer)
    expansion_velocity: Mapped[float] = mapped_column(Float)
    avg_response_hours: Mapped[int] = mapped_column(Integer)
    days_to_renewal: Mapped[int] = mapped_column(Integer)
    health_band: Mapped[str] = mapped_column(String, index=True)
    risk_score: Mapped[float] = mapped_column(Float)

    deals: Mapped[list["Deal"]] = relationship(back_populates="account")


class Deal(Base):
    __tablename__ = "pipeline"

    deal_id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), index=True)
    rep_id: Mapped[str] = mapped_column(ForeignKey("reps.rep_id"), index=True)
    stage: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float)
    stage_weight: Mapped[float] = mapped_column(Float)
    age_days: Mapped[int] = mapped_column(Integer)
    is_stalled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_date: Mapped[str] = mapped_column(String)
    expected_close_date: Mapped[str] = mapped_column(String)
    probability_signal: Mapped[float] = mapped_column(Float)
    won: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ML outputs, pre-computed at ingestion/training and cached for fast reads.
    predicted_win_prob: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)

    account: Mapped["Account"] = relationship(back_populates="deals")
    rep: Mapped["Rep"] = relationship(back_populates="deals")


# Composite index for the Pipeline Overview screen's common filter (stage + account).
Index("ix_pipeline_stage_account", Deal.stage, Deal.account_id)
