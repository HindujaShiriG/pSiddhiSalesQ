"""Inference — apply trained models to deals and cache predictions in SQLite.

Predictions are pre-computed and stored on the Deal rows (predicted_win_prob,
predicted_revenue) so portal reads are fast and don't re-run models per request
(Risk #4 mitigation: pre-compute ML scores on ingestion/refresh).
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from .. import models
from . import features, registry

logger = logging.getLogger("salesiq.ml")


def score_open_deals(session: Session) -> dict:
    """Run both models over the full deal frame and persist per-deal predictions.

    Win probability is scored for every deal; expected revenue is the model's
    predicted amount scaled by win probability (expected realisable value).
    """
    df = features.build_deal_frame(session)
    if df.empty:
        return {"scored": 0}

    win_model, _ = registry.load_model("win_scorer")
    rev_model, _ = registry.load_model("revenue_forecaster")

    win_probs = win_model.predict_proba(df[features.WIN_FEATURES])[:, 1]
    rev_preds = rev_model.predict(df[features.REVENUE_FEATURES])

    deal_ids = df["deal_id"].tolist()
    scored = 0
    for deal_id, wp, rev in zip(deal_ids, win_probs, rev_preds):
        deal = session.get(models.Deal, deal_id)
        if deal is None:
            continue
        # Expected realisable revenue combines both models:
        #   P(win) x model-predicted deal value.
        deal.predicted_win_prob = round(float(wp), 4)
        deal.predicted_revenue = round(float(max(0.0, rev)) * float(wp), 2)
        scored += 1

    session.commit()
    logger.info("Scored %d deals with cached predictions", scored)
    return {"scored": scored}
