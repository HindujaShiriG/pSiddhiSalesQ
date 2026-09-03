"""One-shot pipeline runner: init DB -> ingest -> train -> score.

Handy for local setup, demos, and CI smoke checks:

    python pipeline_cli.py            # full pipeline
    python pipeline_cli.py --ingest   # ingest only
"""
from __future__ import annotations

import argparse
import json

from app.ai import narrative
from app.db import SessionLocal, init_db
from app.integration.ingest import ingest_all
from app.ml import predict
from app.ml import train as trainer


def main() -> None:
    parser = argparse.ArgumentParser(description="SalesIQ pipeline runner.")
    parser.add_argument("--ingest", action="store_true", help="ingest only")
    args = parser.parse_args()

    init_db()
    session = SessionLocal()
    try:
        print("== Ingesting ==")
        summary = ingest_all(session)
        print(f"   accepted={summary.total_accepted} rejected={summary.total_rejected}")
        for r in summary.reports:
            print(f"   {r.domain:9s}: {r.accepted}/{r.received} accepted")
        if args.ingest:
            return

        print("== Training models ==")
        meta = trainer.train_all(session)
        for name, m in meta.items():
            print(f"   {name}: {m['algorithm']} {m['metric']}={m['metric_value']} "
                  f"(meets target: {m['meets_target']})")

        print("== Scoring deals & classifying accounts ==")
        scored = predict.score_open_deals(session)
        classified = predict.predict_account_health(session)
        print(f"   deals scored: {scored}")
        print(f"   accounts classified: {classified}")

        print("== Sample AI narrative (strong_quarter) ==")
        result = narrative.generate(session, "strong_quarter")
        print(f"   source={result['source']}")
        print(json.dumps(result["brief"], indent=2)[:600])
    finally:
        session.close()


if __name__ == "__main__":
    main()
