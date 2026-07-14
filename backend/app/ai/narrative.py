"""AI Sales Intelligence — scenario-based sales narratives.

Design
------
The narrative is grounded in **real** pipeline state and ML outputs (not free
text): the engine assembles a factual brief from SQLite + model predictions,
then asks Gemini 2.5 Flash to turn it into an executive narrative. When no
``GEMINI_API_KEY`` is configured (offline dev, CI), a deterministic
template-based generator produces the same structured narrative from the same
brief — so the feature works end-to-end without network access and QA is stable.

This matches the approved proposal's caching / offline-fallback strategy
(Risk #3) and Ollama-for-offline-dev note.

Phase 1 (mid-term) delivers the **Strong Quarter** scenario. The At-Risk and
Recovery scenarios are Phase-2 (Week-12) deliverables; their briefs are already
computed here so wiring them up later is trivial.
"""
from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..config import settings

logger = logging.getLogger("salesiq.ai")

SCENARIOS = ("strong_quarter", "at_risk_quarter", "recovery")
# Only this scenario is exposed on the portal at mid-term (Week 9).
PHASE1_SCENARIOS = ("strong_quarter",)

try:
    import google.generativeai as genai

    _GENAI = True
except Exception:  # pragma: no cover - optional dependency
    _GENAI = False


def build_brief(session: Session) -> dict:
    """Assemble a factual brief from the unified dataset + cached ML predictions."""
    open_stages = ("Prospecting", "Qualification", "Proposal", "Negotiation")

    total_pipeline = session.query(func.coalesce(func.sum(models.Deal.amount), 0.0)).filter(
        models.Deal.stage.in_(open_stages)
    ).scalar()
    ml_forecast = session.query(func.coalesce(func.sum(models.Deal.predicted_revenue), 0.0)).filter(
        models.Deal.stage.in_(open_stages)
    ).scalar()
    stage_weighted = session.query(
        func.coalesce(func.sum(models.Deal.amount * models.Deal.stage_weight), 0.0)
    ).filter(models.Deal.stage.in_(open_stages)).scalar()

    n_open = session.query(func.count(models.Deal.deal_id)).filter(
        models.Deal.stage.in_(open_stages)
    ).scalar()
    n_stalled = session.query(func.count(models.Deal.deal_id)).filter(
        models.Deal.is_stalled.is_(True)
    ).scalar()

    # Top open deals by expected (ML) revenue.
    top_deals = (
        session.query(models.Deal, models.Account.name)
        .join(models.Account, models.Deal.account_id == models.Account.account_id)
        .filter(models.Deal.stage.in_(open_stages))
        .order_by(models.Deal.predicted_revenue.desc().nullslast())
        .limit(5)
        .all()
    )
    at_risk_accounts = (
        session.query(models.Account)
        .filter(models.Account.health_band != "Healthy")
        .order_by(models.Account.risk_score.desc())
        .limit(5)
        .all()
    )

    return {
        "open_deals": int(n_open or 0),
        "stalled_deals": int(n_stalled or 0),
        "total_pipeline_value": round(float(total_pipeline or 0), 2),
        "stage_weighted_forecast": round(float(stage_weighted or 0), 2),
        "ml_forecast": round(float(ml_forecast or 0), 2),
        "top_deals": [
            {
                "deal_id": d.deal_id,
                "account": acc_name,
                "stage": d.stage,
                "amount": d.amount,
                "win_prob": d.predicted_win_prob,
                "expected_revenue": d.predicted_revenue,
            }
            for d, acc_name in top_deals
        ],
        "at_risk_accounts": [
            {"account_id": a.account_id, "name": a.name, "risk_score": a.risk_score,
             "band": a.health_band, "days_to_renewal": a.days_to_renewal}
            for a in at_risk_accounts
        ],
    }


def _fallback_narrative(scenario: str, brief: dict) -> str:
    """Deterministic, grounded narrative used when Gemini is unavailable."""
    top = brief["top_deals"]
    top_lines = "\n".join(
        f"  • {d['account']} ({d['deal_id']}, {d['stage']}): "
        f"win {int((d['win_prob'] or 0) * 100)}%, expected ₹{int(d['expected_revenue'] or 0):,}"
        for d in top[:3]
    ) or "  • (no open deals)"

    if scenario == "strong_quarter":
        return (
            "STRONG QUARTER — Momentum & Upside\n\n"
            f"The pipeline holds {brief['open_deals']} open deals worth "
            f"₹{int(brief['total_pipeline_value']):,}. The ML revenue forecast is "
            f"₹{int(brief['ml_forecast']):,}, versus a naive stage-weighted figure of "
            f"₹{int(brief['stage_weighted_forecast']):,} — the model's read of rep skill and "
            "account health is the number to plan against.\n\n"
            "Momentum tactics — accelerate the highest-expectation deals:\n"
            f"{top_lines}\n\n"
            "Upsell identification: healthy, high-ARR accounts with positive expansion "
            "velocity are the cleanest stretch-target candidates this quarter.\n\n"
            "Stretch targets: with momentum on the top deals, a stretch above the ML "
            "forecast is defensible — resource the top three deals for acceleration."
        )
    # Briefs for the Phase-2 scenarios are computed; narratives are stubs for now.
    if scenario == "at_risk_quarter":
        risky = ", ".join(a["name"] for a in brief["at_risk_accounts"][:3]) or "none flagged"
        return (
            "AT-RISK QUARTER — Risk Mitigation (Phase 2 preview)\n\n"
            f"{brief['stalled_deals']} deals are stalled and accounts {risky} are trending "
            "unhealthy. Full narrative ships Week 12."
        )
    return (
        "RECOVERY SCENARIO — Priority Ranking (Phase 2 preview)\n\n"
        "Deal re-prioritisation and rep-coaching focus. Full narrative ships Week 12."
    )


def _gemini_narrative(scenario: str, brief: dict) -> str:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = (
        "You are a sales operations analyst. Write a concise executive narrative "
        f"for the '{scenario}' scenario, grounded ONLY in the facts below. "
        "Reference specific deals and accounts by name. Do not invent numbers.\n\n"
        f"FACTS (JSON):\n{brief}\n"
    )
    resp = model.generate_content(prompt)
    return resp.text


def generate(session: Session, scenario: str = "strong_quarter") -> dict:
    """Return a grounded narrative for a scenario, plus the brief and source flag."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario!r}")
    brief = build_brief(session)

    source = "fallback"
    text: str
    if _GENAI and settings.gemini_api_key:
        try:
            text = _gemini_narrative(scenario, brief)
            source = "gemini"
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("Gemini call failed (%s) — using fallback narrative", exc)
            text = _fallback_narrative(scenario, brief)
    else:
        text = _fallback_narrative(scenario, brief)

    return {"scenario": scenario, "source": source, "narrative": text, "brief": brief}
