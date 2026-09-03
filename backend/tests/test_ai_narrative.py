"""Week-9 QA: AI narrative generation (offline fallback) + grounding."""
from __future__ import annotations

import pytest

from app.ai import narrative


def test_brief_is_grounded_in_data(db_session):
    brief = narrative.build_brief(db_session)
    assert brief["open_deals"] >= 0
    assert brief["total_pipeline_value"] >= 0
    assert isinstance(brief["top_deals"], list)


def test_strong_quarter_narrative_offline(db_session):
    result = narrative.generate(db_session, "strong_quarter")
    assert result["scenario"] == "strong_quarter"
    # No GEMINI_API_KEY in CI -> deterministic fallback.
    assert result["source"] == "fallback"
    text = result["narrative"]
    assert "STRONG QUARTER" in text
    # Grounding: the ML forecast figure from the brief appears in the narrative.
    assert "forecast" in text.lower()


def test_at_risk_quarter_narrative_offline(db_session):
    result = narrative.generate(db_session, "at_risk_quarter")
    assert result["scenario"] == "at_risk_quarter"
    assert result["source"] == "fallback"
    text = result["narrative"]
    assert "AT-RISK QUARTER" in text
    assert "risk" in text.lower()


def test_recovery_scenario_narrative_offline(db_session):
    result = narrative.generate(db_session, "recovery")
    assert result["scenario"] == "recovery"
    assert result["source"] == "fallback"
    text = result["narrative"]
    assert "RECOVERY SCENARIO" in text
    assert "triage" in text.lower() or "recovery" in text.lower()


def test_unknown_scenario_raises(db_session):
    with pytest.raises(ValueError):
        narrative.generate(db_session, "not_a_scenario")


def test_intelligence_endpoint(client):
    for scen in ("strong_quarter", "at_risk_quarter", "recovery"):
        r = client.get(f"/api/intelligence/narrative?scenario={scen}")
        assert r.status_code == 200
        body = r.json()
        assert body["scenario"] == scen
        assert len(body["narrative"]) > 50


def test_scenarios_endpoint(client):
    r = client.get("/api/intelligence/scenarios")
    assert r.status_code == 200
    available = r.json()["available"]
    assert "strong_quarter" in available
    assert "at_risk_quarter" in available
    assert "recovery" in available

