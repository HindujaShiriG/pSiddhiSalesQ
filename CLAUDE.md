# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this project is

**SalesIQ** — a unified, AI-powered sales operations system built for the IMPACT
pSiddhi Semester 4 capstone (RFP S4-I-21). It integrates CRM data from three
domains, runs three ML models, generates AI narratives, and surfaces everything
through a 4-screen React portal deployed on Azure.

Authoritative planning docs — read these before making design decisions:
- [Solution_proposal.md](Solution_proposal.md) — the accepted proposal (scope of truth)
- [Implementation.md](Implementation.md) — weekly build plan and deliverables
- [README.md](README.md) — architecture, layout, and setup

## Hard constraints (do not violate)

- **Budget ceiling ₹2,500.** Prefer free / open-source / free-tier tools. Only
  Azure Backend Hosting (₹800) and a ₹500 contingency buffer are paid. Do not
  introduce a paid dependency without flagging the cost trade-off.
- **AI is the operational core, not cosmetic.** ML models must drive real decisions
  (win scoring, forecasting, health classification). Gemini is used **only** for
  narrative generation — never for numeric prediction.
- **QA is mandatory and embedded**, not bolted on at the end. Every feature ships
  with tests. Target **≥80% coverage**.
- **ML accuracy targets are acceptance criteria:** Revenue MAPE < 15%, Win
  AUC-ROC > 0.75, Health F1 > 0.75. Track everything in MLflow.

## Tech stack

| Concern | Choice |
|---|---|
| Backend / API | Python + **FastAPI** |
| Database | **SQLite** (embedded, zero-config) |
| Mock CRM | **JSON Server** (3 REST domains) |
| ML | **scikit-learn**, **PyCaret** (auto model select), **MLflow** (tracking) |
| AI narratives | **Google Gemini 2.5 Flash** (free tier); **Ollama + Llama 4 Scout** for offline dev |
| Frontend | **React** + **Recharts** |
| Data generation | **Faker** (500+ synthetic records) |
| Hosting | Azure Static Web Apps (Free) + Azure App Service F1 (Linux) |
| QA | **pytest**, **pytest-cov**, **Playwright**, **httpx** |
| CI/CD | **GitHub Actions** |

## Architecture flow

```
JSON Server → FastAPI (validate) → SQLite → [ML models + Gemini] → React portal (Azure)
```

Three CRM domains: **pipeline**, **account health**, **rep performance**.
Four portal screens: **Pipeline Overview**, **Account Detail**, **Rep Performance**, **AI Intelligence**.
Three AI scenarios: **Strong Quarter**, **At-Risk Quarter**, **Recovery**.

## Directory conventions

- `backend/` — FastAPI app, ML engine, AI engine. Keep API routing, ML inference,
  and AI narrative generation in separate modules.
- `frontend/` — React portal, one component tree per screen.
- `data/` — JSON Server db, Faker generators, SQLite file. Synthetic data only.
- `docs/` — proposal and reference material (do not edit the source `.docx`).

## Working commands

```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000
pytest --cov=app --cov-report=term-missing

# Frontend
cd frontend && npm run dev
npx playwright test

# Mock CRM
cd data && json-server --watch crm_db.json --port 3001
```

## Conventions & expectations

- **Schema validation on ingestion.** Records missing required fields are logged
  and excluded from ML inference — never silently passed through.
- **Pre-compute ML scores at ingestion** where possible; the portal should render
  fast (target < 3s per screen). Add SQLite indexes on hot columns.
- **Cache Gemini narratives** — free-tier rate limits are real. Pre-generate before
  demos; fall back to cached output rather than failing live.
- Match existing code style within each directory. Python is the primary language
  for backend, ML, and data.
- Never commit secrets. `GEMINI_API_KEY` comes from the environment.

## When unsure

Defer to `Solution_proposal.md`. If a request conflicts with the budget ceiling,
the AI-core mandate, or the QA/coverage requirement, flag it before proceeding.
