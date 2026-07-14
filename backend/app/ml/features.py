"""Feature engineering — build model-ready frames from the unified SQLite dataset.

Each deal is joined to its rep and account so the models can learn from
cross-domain signal (rep skill, account health) rather than deal attributes
alone. This is the whole point of the unified dataset.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from .. import models

# Feature design (avoids target leakage)
# --------------------------------------------------------------------------- #
# `stage`/`stage_weight` are EXCLUDED from the win model: for closed deals the
# stage is literally "Closed Won"/"Closed Lost", which would leak the label.
# `amount` is EXCLUDED from the revenue model: realised revenue == amount for
# won deals, so including it would make the regression trivial/circular.
# Both models therefore learn from genuine context — rep skill, account health,
# deal age — which is the point of the unified dataset.
BASE_NUMERIC = [
    "age_days",
    "is_stalled",
    "rep_win_rate",
    "rep_attainment",
    "rep_cycle_days",
    "account_engagement",
    "account_tickets",
    "account_risk",
    "account_response_hours",
]
BASE_CATEGORICAL = ["segment", "industry"]

# Win-probability model: context + deal size, but NOT the closing stage.
WIN_NUMERIC = BASE_NUMERIC + ["amount"]
WIN_CATEGORICAL = BASE_CATEGORICAL
WIN_FEATURES = WIN_NUMERIC + WIN_CATEGORICAL

# Revenue model: predict a deal's realisable value from context, NOT its amount.
REVENUE_NUMERIC = BASE_NUMERIC
REVENUE_CATEGORICAL = BASE_CATEGORICAL
REVENUE_FEATURES = REVENUE_NUMERIC + REVENUE_CATEGORICAL

# Union used when materialising the feature frame from SQLite.
ALL_FEATURES = sorted(set(WIN_FEATURES) | set(REVENUE_FEATURES) | {"amount"})


def build_deal_frame(session: Session) -> pd.DataFrame:
    """Return one row per deal with joined rep + account features."""
    q = (
        session.query(
            models.Deal.deal_id,
            models.Deal.stage,
            models.Deal.amount,
            models.Deal.stage_weight,
            models.Deal.age_days,
            models.Deal.is_stalled,
            models.Deal.won,
            models.Rep.historical_win_rate.label("rep_win_rate"),
            models.Rep.attainment_pct.label("rep_attainment"),
            models.Rep.avg_deal_cycle_days.label("rep_cycle_days"),
            models.Account.engagement_score.label("account_engagement"),
            models.Account.support_tickets_30d.label("account_tickets"),
            models.Account.risk_score.label("account_risk"),
            models.Account.avg_response_hours.label("account_response_hours"),
            models.Account.segment,
            models.Account.industry,
        )
        .join(models.Rep, models.Deal.rep_id == models.Rep.rep_id)
        .join(models.Account, models.Deal.account_id == models.Account.account_id)
    )
    df = pd.read_sql(q.statement, session.bind)
    if not df.empty:
        df["is_stalled"] = df["is_stalled"].astype(int)
    return df


def win_training_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Closed deals only (won in {0,1}) — supervised set for win-probability."""
    closed = df[df["won"].notna()].copy()
    y = closed["won"].astype(int)
    X = closed[WIN_FEATURES].copy()
    return X, y


def revenue_training_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Closed-won deals — realised revenue (== amount) is the regression target.

    The model learns to predict a deal's realisable value from context features
    (rep, account, age) WITHOUT seeing the amount itself, then generalises to
    open deals as an expected-value estimate.
    """
    won = df[df["won"] == 1].copy()
    y = won["amount"].astype(float)
    X = won[REVENUE_FEATURES].copy()
    return X, y
