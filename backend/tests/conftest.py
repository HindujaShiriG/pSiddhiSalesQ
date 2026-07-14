"""Test bootstrap.

Environment is redirected to an isolated temp SQLite DB + a freshly generated
CRM fixture file *before* any app module is imported, so tests never touch the
developer's real database or models. The CRM base URL points at a dead port so
the integration layer exercises its file-fallback path deterministically.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
_TMP = Path(tempfile.mkdtemp(prefix="salesiq_test_"))
_CRM_FILE = _TMP / "crm_db.json"


def _generate_fixture_data() -> None:
    """Build a compact, reproducible CRM dataset using the real Faker generator."""
    spec = importlib.util.spec_from_file_location("gen_data", ROOT_DIR / "data" / "generate_data.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    reps = gen.generate_reps(30)
    accounts = gen.generate_accounts(80)
    deals, _ = gen.generate_deals(400, reps, accounts, drop_rate=0.03)
    _CRM_FILE.write_text(json.dumps({"pipeline": deals, "accounts": accounts, "reps": reps}))


_generate_fixture_data()

# Redirect config via env BEFORE importing the app (pydantic-settings reads these).
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"
os.environ["CRM_FALLBACK_FILE"] = str(_CRM_FILE)
os.environ["CRM_BASE_URL"] = "http://127.0.0.1:59999"  # nothing listening -> fast fallback
os.environ["MODEL_DIR"] = str(_TMP / "models")
os.environ["MLFLOW_TRACKING_URI"] = f"file:{(_TMP / 'mlruns').as_posix()}"

from app.db import SessionLocal, init_db  # noqa: E402
from app.integration.ingest import ingest_all  # noqa: E402
from app.ml import predict  # noqa: E402
from app.ml import train as trainer  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _bootstrap():
    """Init DB, ingest the fixture data, train both models, and score deals once."""
    init_db()
    session = SessionLocal()
    try:
        ingest_all(session)
        trainer.train_all(session)
        predict.score_open_deals(session)
    finally:
        session.close()
    yield


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def crm_file() -> Path:
    return _CRM_FILE
