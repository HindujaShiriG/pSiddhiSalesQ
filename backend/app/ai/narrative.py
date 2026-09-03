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
AVAILABLE_SCENARIOS = ("strong_quarter", "at_risk_quarter", "recovery")
# Kept for backward compatibility with mid-term tests/references
PHASE1_SCENARIOS = AVAILABLE_SCENARIOS

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
        f"win probability {int((d['win_prob'] or 0) * 100)}%, expected revenue ₹{int(d['expected_revenue'] or 0):,}"
        for d in top[:3]
    ) or "  • (no open deals)"

    risky = ", ".join(a["name"] for a in brief["at_risk_accounts"][:3]) or "None flagged"
    risky_detail = "\n".join(
        f"  • {a['name']} (Risk: {int(a['risk_score'] * 100)}%, Band: {a['band']}, Renewal in {a['days_to_renewal']}d)"
        for a in brief["at_risk_accounts"][:3]
    ) or "  • (no high-risk accounts)"

    if scenario == "strong_quarter":
        return (
            "STRONG QUARTER — Momentum & Upside Execution\n\n"
            f"The pipeline holds {brief['open_deals']} open deals worth "
            f"₹{int(brief['total_pipeline_value']):,}. The ML revenue forecast is "
            f"₹{int(brief['ml_forecast']):,}, versus a naive stage-weighted baseline of "
            f"₹{int(brief['stage_weighted_forecast']):,} — the ML model's cross-domain evaluation "
            "of rep win rates and account health provides the statistically grounded target to commit against.\n\n"
            "Momentum Tactics — Accelerate highest expected-value opportunities:\n"
            f"{top_lines}\n\n"
            "Upsell Identification:\n"
            "Healthy accounts in Enterprise and Mid-Market sectors with positive expansion velocity represent "
            "prime candidates for mid-cycle expansion and multi-year contract renewals.\n\n"
            "Stretch Target Commitment:\n"
            f"With strong deal velocity and {brief['stalled_deals']} stalled deals, leadership can defensibly set "
            f"a stretch target 10-15% above the ML baseline of ₹{int(brief['ml_forecast']):,} by deploying executive "
            "sponsors to the top three pipeline deals."
        )

    if scenario == "at_risk_quarter":
        return (
            "AT-RISK QUARTER — Risk Mitigation & Churn Defense\n\n"
            f"Executive Warning: Pipeline analysis identifies {brief['stalled_deals']} stalled opportunities "
            f"out of {brief['open_deals']} total open deals. The ML forecast indicates potential revenue slippage "
            f"with expected realization at ₹{int(brief['ml_forecast']):,}.\n\n"
            "Account Churn Defense — High-Risk Renewal Watchlist:\n"
            f"{risky_detail}\n\n"
            "Risk Mitigation Playbook:\n"
            "1. Stalled Deal Interventions: Conduct immediate deal triage on opportunities inactive for >30 days. "
            "Re-qualify decision-makers and unblock technical objections.\n"
            f"2. Customer Retention: Accounts {risky} require immediate Customer Success leadership check-ins "
            "to address open support tickets and reverse declining engagement before contract renewals.\n"
            "3. Pipeline Coverage Defense: Mandate 3.5x pipeline coverage for all reps tracking below 80% quota attainment."
        )

    # Recovery scenario
    return (
        "RECOVERY SCENARIO — Deal Triage & Operational Acceleration\n\n"
        f"Operational Recovery Plan: Addressing current pipeline deficit against targets. Active pipeline holds "
        f"{brief['open_deals']} open deals valued at ₹{int(brief['total_pipeline_value']):,}, with an ML forecast "
        f"of ₹{int(brief['ml_forecast']):,}.\n\n"
        "Priority Triage — High-Probability Quick-Win Opportunities:\n"
        f"{top_lines}\n\n"
        "Rep Coaching & Resource Reallocation:\n"
        "Pair high-win-rate senior reps as co-pilots on stalled opportunities in Proposal and Negotiation stages. "
        "Shift sales engineering resources toward deals with win probability > 60%.\n\n"
        "Actionable Recovery Milestones:\n"
        f"1. Executive alignment calls on the top 3 high-value deals within the next 10 business days.\n"
        f"2. Resolve critical support tickets for at-risk accounts ({risky}) to safeguard baseline ARR.\n"
        "3. Implement daily deal desk reviews to fast-track contract approvals and close the quarterly revenue gap."
    )


def _gemini_narrative(scenario: str, brief: dict) -> str:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = (
        "You are an executive sales operations director. Write an authoritative, structured, and actionable "
        f"executive narrative for the '{scenario}' scenario, grounded STRICTLY in the factual CRM and ML metrics below. "
        "Reference specific deals, account names, and financial figures provided. Do not fabricate any numbers.\n\n"
        f"SCENARIO FOCUS:\n"
        "- If strong_quarter: Focus on momentum tactics, deal acceleration, expansion, and stretch goals.\n"
        "- If at_risk_quarter: Focus on risk mitigation, stalled deals, account churn defense, and pipeline protection.\n"
        "- If recovery: Focus on priority triage, rep coaching focus, quick-win closures, and deal desk acceleration.\n\n"
        f"CRM & ML FACTS (JSON):\n{brief}\n"
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
