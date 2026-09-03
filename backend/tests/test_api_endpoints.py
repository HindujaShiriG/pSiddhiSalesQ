"""Week-7 QA: FastAPI endpoint schema + response tests."""
from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_pipeline_overview_shape(client):
    r = client.get("/api/pipeline/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["total_deals"] > 0
    assert body["stage_weighted_forecast"] >= 0
    assert isinstance(body["stages"], list) and len(body["stages"]) > 0
    for stage in body["stages"]:
        assert {"stage", "count", "total_amount", "weighted_amount"} <= stage.keys()


def test_pipeline_deals_filter(client):
    r = client.get("/api/pipeline/deals?stage=Proposal&limit=10")
    assert r.status_code == 200
    deals = r.json()
    assert all(d["stage"] == "Proposal" for d in deals)


def test_accounts_list_and_detail(client):
    lst = client.get("/api/accounts?limit=5")
    assert lst.status_code == 200
    accounts = lst.json()
    assert len(accounts) > 0

    account_id = accounts[0]["account_id"]
    detail = client.get(f"/api/accounts/{account_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["account"]["account_id"] == account_id
    assert "deals" in body


def test_account_not_found(client):
    r = client.get("/api/accounts/DOES-NOT-EXIST")
    assert r.status_code == 404


def test_reps_endpoint(client):
    r = client.get("/api/reps?limit=5")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_admin_model_status(client):
    r = client.get("/api/admin/models")
    assert r.status_code == 200
    body = r.json()
    assert "win_scorer" in body
    assert "revenue_forecaster" in body
    assert "health_classifier" in body


def test_admin_score(client):
    r = client.post("/api/admin/score")
    assert r.status_code == 200
    body = r.json()
    assert "deals" in body
    assert "accounts" in body

