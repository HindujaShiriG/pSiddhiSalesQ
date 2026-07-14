"""Week 5/6 QA: integration + data-integrity across all 3 CRM domains."""
from __future__ import annotations

import json

from app import models
from app.integration.crm_client import CRMClient
from app.integration.ingest import ingest_all


def test_all_three_domains_ingested(db_session):
    assert db_session.query(models.Rep).count() > 0
    assert db_session.query(models.Account).count() > 0
    assert db_session.query(models.Deal).count() > 0


def test_invalid_records_excluded(db_session, crm_file):
    """Rejected deals (missing fields) must not appear in the unified dataset."""
    raw = json.loads(crm_file.read_text())
    raw_deals = len(raw["pipeline"])
    stored_deals = db_session.query(models.Deal).count()
    # Some raw deals were intentionally invalid, so stored < raw.
    assert stored_deals < raw_deals
    assert stored_deals > 0


def test_referential_integrity(db_session):
    """Every stored deal references an existing account and rep."""
    account_ids = {a.account_id for a in db_session.query(models.Account.account_id)}
    rep_ids = {r.rep_id for r in db_session.query(models.Rep.rep_id)}
    for deal in db_session.query(models.Deal).all():
        assert deal.account_id in account_ids
        assert deal.rep_id in rep_ids


def test_ingest_report_counts(db_session):
    summary = ingest_all(db_session)
    assert summary.total_accepted > 0
    assert {r.domain for r in summary.reports} == {"reps", "accounts", "pipeline"}
    for r in summary.reports:
        assert r.received == r.accepted + r.rejected


def test_client_falls_back_to_file(crm_file):
    """With a dead base URL, the client transparently reads the fixture file."""
    client = CRMClient(base_url="http://127.0.0.1:59999", fallback_file=str(crm_file))
    reps = client.fetch("reps")
    assert isinstance(reps, list) and len(reps) > 0
