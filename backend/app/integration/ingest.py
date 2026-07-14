"""Ingestion pipeline: validate each record against its schema, normalise, and
upsert into SQLite. Invalid records are counted, logged, and excluded — never
written to the unified dataset (and therefore never seen by the ML engine).

Ingestion order matters for referential integrity: reps and accounts first,
then deals (which reference both). Deals whose FK targets were rejected are
themselves dropped.
"""
from __future__ import annotations

import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import models
from ..schemas import AccountIn, DealIn, IngestReport, IngestSummary, RepIn
from .crm_client import CRMClient

logger = logging.getLogger("salesiq.integration")

_MAX_ERRORS_KEPT = 10  # cap error list per domain to keep the report readable


def _short_error(record_id: str, exc: ValidationError) -> str:
    first = exc.errors()[0]
    loc = ".".join(str(p) for p in first["loc"])
    return f"{record_id}: {loc} — {first['msg']}"


def _ingest_reps(session: Session, raw: list[dict]) -> IngestReport:
    accepted, errors = 0, []
    for rec in raw:
        rid = str(rec.get("rep_id", "?"))
        try:
            rep = RepIn(**rec)
        except ValidationError as exc:
            if len(errors) < _MAX_ERRORS_KEPT:
                errors.append(_short_error(rid, exc))
            continue
        session.merge(models.Rep(**rep.model_dump()))
        accepted += 1
    return IngestReport(domain="reps", received=len(raw), accepted=accepted,
                        rejected=len(raw) - accepted, errors=errors)


def _ingest_accounts(session: Session, raw: list[dict]) -> IngestReport:
    accepted, errors = 0, []
    for rec in raw:
        aid = str(rec.get("account_id", "?"))
        try:
            acc = AccountIn(**rec)
        except ValidationError as exc:
            if len(errors) < _MAX_ERRORS_KEPT:
                errors.append(_short_error(aid, exc))
            continue
        session.merge(models.Account(**acc.model_dump()))
        accepted += 1
    return IngestReport(domain="accounts", received=len(raw), accepted=accepted,
                        rejected=len(raw) - accepted, errors=errors)


def _ingest_deals(session: Session, raw: list[dict],
                  valid_accounts: set[str], valid_reps: set[str]) -> IngestReport:
    accepted, errors = 0, []
    for rec in raw:
        did = str(rec.get("deal_id", "?"))
        try:
            deal = DealIn(**rec)
        except ValidationError as exc:
            if len(errors) < _MAX_ERRORS_KEPT:
                errors.append(_short_error(did, exc))
            continue
        # Referential integrity: drop deals pointing at rejected/absent FKs.
        if deal.account_id not in valid_accounts or deal.rep_id not in valid_reps:
            if len(errors) < _MAX_ERRORS_KEPT:
                errors.append(f"{did}: dangling FK (account/rep not in unified set)")
            continue
        session.merge(models.Deal(**deal.model_dump()))
        accepted += 1
    return IngestReport(domain="pipeline", received=len(raw), accepted=accepted,
                        rejected=len(raw) - accepted, errors=errors)


def ingest_all(session: Session, client: CRMClient | None = None) -> IngestSummary:
    """Fetch all domains and persist the validated, normalised unified dataset."""
    client = client or CRMClient()
    raw = client.fetch_all()

    rep_report = _ingest_reps(session, raw["reps"])
    acc_report = _ingest_accounts(session, raw["accounts"])
    session.flush()

    valid_reps = {r.rep_id for r in session.query(models.Rep.rep_id).all()}
    valid_accounts = {a.account_id for a in session.query(models.Account.account_id).all()}
    deal_report = _ingest_deals(session, raw["pipeline"], valid_accounts, valid_reps)

    session.commit()

    reports = [rep_report, acc_report, deal_report]
    summary = IngestSummary(
        reports=reports,
        total_accepted=sum(r.accepted for r in reports),
        total_rejected=sum(r.rejected for r in reports),
    )
    logger.info(
        "Ingestion complete: %d accepted, %d rejected",
        summary.total_accepted, summary.total_rejected,
    )
    return summary
