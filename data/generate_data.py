"""
SalesIQ — Synthetic CRM data generator (Faker).

Produces 500+ records across the three CRM domains the platform integrates:
  - pipeline        (deals / opportunities)
  - accounts        (account-health signals)
  - reps            (rep performance)

Output is written as a single JSON Server database file (``crm_db.json``) that
exposes one REST collection per domain. The FastAPI integration layer ingests
from these endpoints (or directly from this file as a fallback).

Design notes
------------
* Data is generated with a **fixed seed** so runs are reproducible and QA
  assertions on record counts / distributions are stable.
* Realistic variance is intentionally injected (stalled deals, disengaged
  accounts, low-win-rate reps) so the ML models have a signal to learn and the
  AI narratives have real scenarios to describe. This directly addresses
  Risk #1 in the approved proposal (ML accuracy on synthetic data).
* A small, deliberate fraction of records are emitted with missing required
  fields so the schema-validation layer has invalid records to reject
  (exercised by the Week-4 schema-validation tests).

Usage
-----
    python generate_data.py                 # writes crm_db.json (defaults)
    python generate_data.py --reps 40 --accounts 120 --deals 400
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

# Fixed seed => reproducible dataset (stable QA assertions).
SEED = 4021
fake = Faker()
Faker.seed(SEED)

HERE = Path(__file__).resolve().parent

PIPELINE_STAGES = [
    "Prospecting",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]
# Fixed stage weights — the naive forecast the ML engine is meant to beat.
STAGE_WEIGHTS = {
    "Prospecting": 0.10,
    "Qualification": 0.25,
    "Proposal": 0.50,
    "Negotiation": 0.75,
    "Closed Won": 1.00,
    "Closed Lost": 0.00,
}
INDUSTRIES = ["SaaS", "Fintech", "Healthcare", "Retail", "Manufacturing", "Logistics", "EdTech"]
REGIONS = ["North", "South", "East", "West"]
SEGMENTS = ["Enterprise", "Mid-Market", "SMB"]
HEALTH_BANDS = ["Healthy", "At-Risk", "Critical"]

# Reference "today" for the synthetic world — fixed so date maths is deterministic.
TODAY = date(2026, 7, 1)


def _rng(n: int):
    """Deterministic pseudo-random floats in [0, 1) derived from Faker's seeded RNG."""
    return [fake.pyfloat(min_value=0, max_value=1, right_digits=4) for _ in range(n)]


def generate_reps(n_reps: int) -> list[dict]:
    reps = []
    for i in range(1, n_reps + 1):
        # Give each rep a stable "skill" that correlates with win rate — signal for ML.
        skill = fake.pyfloat(min_value=0.2, max_value=0.95, right_digits=2)
        quota = fake.random_int(min=800_000, max=3_000_000, step=50_000)
        attainment = round(max(0.0, min(1.6, skill + fake.pyfloat(min_value=-0.25, max_value=0.35, right_digits=2))), 2)
        reps.append(
            {
                "rep_id": f"R{i:03d}",
                "name": fake.name(),
                "region": fake.random_element(REGIONS),
                "segment": fake.random_element(SEGMENTS),
                "tenure_months": fake.random_int(min=3, max=120),
                "quota": quota,
                "attainment_pct": attainment,           # fraction of quota attained
                "historical_win_rate": round(skill, 2),  # 0..1 — key ML feature
                "activities_last_30d": fake.random_int(min=5, max=140),
                "avg_deal_cycle_days": fake.random_int(min=25, max=160),
            }
        )
    return reps


def generate_accounts(n_accounts: int) -> list[dict]:
    accounts = []
    for i in range(1, n_accounts + 1):
        engagement = fake.pyfloat(min_value=0.05, max_value=1.0, right_digits=2)
        tickets = fake.random_int(min=0, max=45)
        # Health degrades with low engagement and high ticket volume.
        risk_score = round(min(1.0, max(0.0, (1 - engagement) * 0.6 + (tickets / 45) * 0.4)), 2)
        if risk_score < 0.35:
            band = "Healthy"
        elif risk_score < 0.65:
            band = "At-Risk"
        else:
            band = "Critical"
        renewal_in = fake.random_int(min=10, max=340)
        accounts.append(
            {
                "account_id": f"A{i:04d}",
                "name": fake.company(),
                "industry": fake.random_element(INDUSTRIES),
                "region": fake.random_element(REGIONS),
                "segment": fake.random_element(SEGMENTS),
                "arr": fake.random_int(min=120_000, max=4_500_000, step=10_000),
                "engagement_score": engagement,             # 0..1
                "support_tickets_30d": tickets,
                "expansion_velocity": fake.pyfloat(min_value=-0.2, max_value=0.5, right_digits=2),
                "avg_response_hours": fake.random_int(min=1, max=96),
                "days_to_renewal": renewal_in,
                "health_band": band,                        # label for the classifier (Wk11)
                "risk_score": risk_score,
            }
        )
    return accounts


def generate_deals(n_deals: int, reps: list[dict], accounts: list[dict], drop_rate: float) -> list[dict]:
    deals = []
    n_invalid = 0
    # Deterministic invalid-record injection: every `stride`-th deal gets a
    # required field nulled, so the schema-validation layer always has invalid
    # records to reject (reproducible across runs).
    stride = max(1, round(1 / drop_rate)) if drop_rate > 0 else 0
    # Deal size is largely driven by account segment (a model feature), so the
    # revenue forecaster has learnable structure rather than pure noise.
    seg_base = {"Enterprise": 850_000, "Mid-Market": 420_000, "SMB": 160_000}
    for i in range(1, n_deals + 1):
        rep = fake.random_element(reps)
        account = fake.random_element(accounts)
        age_days = fake.random_int(min=1, max=180)

        # ---- Deal size: f(segment, engagement, rep attainment) + mild noise ----
        base = seg_base[account["segment"]]
        modifier = (
            (0.85 + 0.30 * account["engagement_score"])      # engaged accounts buy bigger
            * (0.90 + 0.20 * min(1.0, rep["attainment_pct"]))  # strong reps land bigger
        )
        noise = fake.pyfloat(min_value=0.92, max_value=1.08, right_digits=3)
        amount = int(round(base * modifier * noise / 5000.0)) * 5000

        # ---- Win score: f(rep skill, account health, size) ----
        # The outcome is a well-separated threshold on this score (plus mild
        # noise), so the win-probability model recovers a strong, non-trivial
        # signal from rep skill and account health (target AUC > 0.75).
        win_score = (
            0.85 * rep["historical_win_rate"]
            + 0.15 * account["engagement_score"]
            - 0.18 * account["risk_score"]
            - 0.05 * (amount > 700_000)         # bigger deals are harder
        )
        noisy_score = win_score + fake.pyfloat(min_value=-0.12, max_value=0.12, right_digits=3)

        # ---- Stage / open-vs-closed, coherent with the outcome ----
        # ~50% of deals are closed; the rest are live pipeline.
        is_closed = fake.pyfloat(min_value=0, max_value=1, right_digits=3) < 0.50
        if is_closed:
            won = 1 if noisy_score > 0.48 else 0   # threshold near the score median
            stage = "Closed Won" if won else "Closed Lost"
            stalled = False
        else:
            won = None
            stage = fake.random_element(["Prospecting", "Qualification", "Proposal", "Negotiation"])
            stalled = age_days > 45 and stage in ("Proposal", "Qualification", "Prospecting")

        created = TODAY - timedelta(days=age_days)
        close_offset = fake.random_int(min=-20, max=90)
        expected_close = TODAY + timedelta(days=close_offset)

        deal = {
            "deal_id": f"D{i:05d}",
            "account_id": account["account_id"],
            "rep_id": rep["rep_id"],
            "stage": stage,
            "amount": amount,
            "stage_weight": STAGE_WEIGHTS[stage],
            "age_days": age_days,
            "is_stalled": stalled,
            "created_date": created.isoformat(),
            "expected_close_date": expected_close.isoformat(),
            "probability_signal": round(max(0.0, min(1.0, win_score)), 3),
            "won": won,
        }

        # Inject a small fraction of invalid records (missing required field)
        # so the schema-validation layer has something to reject.
        if stride and i % stride == 0:
            n_invalid += 1
            field = fake.random_element(["amount", "stage", "account_id"])
            deal[field] = None
        deals.append(deal)

    return deals, n_invalid


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic SalesIQ CRM data.")
    parser.add_argument("--reps", type=int, default=40)
    parser.add_argument("--accounts", type=int, default=120)
    parser.add_argument("--deals", type=int, default=500)
    parser.add_argument("--drop-rate", type=float, default=0.03,
                        help="Fraction of deals emitted with a missing required field.")
    parser.add_argument("--out", type=str, default=str(HERE / "crm_db.json"))
    args = parser.parse_args()

    reps = generate_reps(args.reps)
    accounts = generate_accounts(args.accounts)
    deals, n_invalid = generate_deals(args.deals, reps, accounts, args.drop_rate)

    db = {"pipeline": deals, "accounts": accounts, "reps": reps}
    total = len(deals) + len(accounts) + len(reps)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(db, indent=2), encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"  pipeline (deals): {len(deals)}  ({n_invalid} intentionally invalid)")
    print(f"  accounts        : {len(accounts)}")
    print(f"  reps            : {len(reps)}")
    print(f"  TOTAL records   : {total}  (target >= 500: {'OK' if total >= 500 else 'LOW'})")


if __name__ == "__main__":
    main()
