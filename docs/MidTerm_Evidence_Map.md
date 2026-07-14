# SalesIQ — Mid-Term Evidence Map (Weeks 4–9)

Maps each approved Phase-1 deliverable to the code, tests, and commands that
prove it — a scaffold for filling `pSiddhi3_0_MidTerm_Submission_Template.docx`
(Sections 3, 4, and 6). All metrics below are from the seeded synthetic dataset
and reproduce on `python pipeline_cli.py`.

## Progress against approved plan (template Section 3)

| ID | Deliverable (approved) | Window | Status | Where it lives / how to prove it |
|---|---|---|---|---|
| D-01 | JSON Server mock CRM + unified schema + FastAPI scaffold | Wk 4 | **Done** | [data/generate_data.py](../data/generate_data.py), [data/crm_db.json](../data/crm_db.json), [backend/app/schemas.py](../backend/app/schemas.py), [backend/app/main.py](../backend/app/main.py) · test: `tests/test_schema_validation.py` |
| D-02 | FastAPI integration for pipeline + rep domains → SQLite | Wk 5 | **Done** | [backend/app/integration/](../backend/app/integration/), [backend/app/models.py](../backend/app/models.py) · test: `tests/test_integration_ingest.py` |
| D-03 | Account-health domain; all 3 domains normalised & queryable | Wk 6 | **Done** | `integration/ingest.py` (3 domains + referential integrity) · tests: `test_all_three_domains_ingested`, `test_referential_integrity` |
| D-04 | React portal — Pipeline Overview + Account Detail; API endpoints | Wk 7 | **Done** | [frontend/src/screens/](../frontend/src/screens/), [backend/app/routers/pipeline.py](../backend/app/routers/pipeline.py), `routers/accounts.py` · test: `tests/test_api_endpoints.py` |
| D-05 | Revenue Forecaster + Win Probability Scorer; MLflow tracking | Wk 8 | **Done** | [backend/app/ml/](../backend/app/ml/) · test: `tests/test_ml_models.py` · MLflow runs in `backend/mlruns/` |
| D-06 | Gemini connected; initial AI narrative (1 scenario) | Wk 9 | **Done** | [backend/app/ai/narrative.py](../backend/app/ai/narrative.py), `routers/intelligence.py` · test: `tests/test_ai_narrative.py` |

### Week-10 checkpoint self-assessment (template Section 3.1)
- **Checkpoint:** data layer + portal foundation + initial AI, all QA passing.
- **% complete:** ~100% of the Phase-1 (Wk 4–9) scope; Phase-2 items (3rd model,
  remaining 2 screens, all 3 AI scenarios, Azure deploy) are correctly *not* claimed.
- **Demonstrable live:** Yes, end-to-end (`uvicorn` + `npm run dev`).

## Measured results (reproducible)

| Metric | Result | Target | Source |
|---|---|---|---|
| Records generated | 660 (500 deals + 120 accounts + 40 reps) | ≥ 500 | `python data/generate_data.py` |
| Invalid records rejected on ingest | 15 deals | > 0 | ingest report / `test_invalid_records_excluded` |
| Win Probability Scorer AUC-ROC | **0.96** | > 0.75 | `GET /api/admin/models` |
| Revenue Forecaster MAPE | **0.054** | < 0.15 | `GET /api/admin/models` |
| Backend test coverage | **93%** (28 tests) | ≥ 80% | `pytest --cov=app` |

## QA progress (template Section 6)

| Test type | Written/run | Coverage | Target | File |
|---|---|---|---|---|
| Unit (schema validation) | 6 | part of 93% | >80% | `test_schema_validation.py` |
| Integration (3 domains) | 5 | " | all 3 domains | `test_integration_ingest.py` |
| API endpoint | 7 | " | all screens' APIs | `test_api_endpoints.py` |
| ML accuracy/range | 5 | " | targets met | `test_ml_models.py` |
| AI narrative | 5 | " | scenario 1 | `test_ai_narrative.py` |

## Suggested evidence captures (template Section 4)

- **EV-01** `python data/generate_data.py` output (660 records, 15 invalid).
- **EV-02** `pipeline_cli.py` output showing ingest counts + both model metrics.
- **EV-03** `pytest --cov=app` summary (28 passed, 93% coverage).
- **EV-04** `GET /api/pipeline/overview` JSON (ML forecast vs stage-weighted).
- **EV-05** Portal screenshot — Pipeline Overview (stage chart + top deals).
- **EV-06** Portal screenshot — Account Detail (health mix + deals).
- **EV-07** AI Intelligence narrative response (`/api/intelligence/narrative`).
- **EV-08** MLflow runs in `backend/mlruns/` (params + metrics logged).

## Deviations to disclose (template Section 8)

| Item | Approved | Actual | Reason |
|---|---|---|---|
| Model auto-select | PyCaret | scikit-learn compare-and-select | PyCaret dependency pins incompatible with Python 3.13; same behaviour + candidate algorithms retained; MLflow unchanged |
| Gemini narratives | Gemini 2.5 Flash | Gemini + deterministic offline fallback | Free-tier/rate-limit + offline dev (Risk #3); fallback grounded in same ML brief |
