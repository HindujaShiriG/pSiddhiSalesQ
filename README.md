# SalesIQ — Unified Sales Operations System

> **RFP:** S4-I-21 · IMPACT pSiddhi Semester 4 — Integration Mastery (Capstone)
> **Author:** Hindujashiri Gopu (P403) · **Budget:** ₹2,500 ceiling (₹1,300 estimated)

SalesIQ is a unified, AI-powered sales operations platform that eliminates four
compounding failure modes in the sales function: corrupted CRM inputs, stage-weighted
forecast inaccuracy, invisible account-health signals, and the absence of ML
intelligence across the sales cycle.

See [Solution_proposal.md](Solution_proposal.md) for the full proposal and
[Implementation.md](Implementation.md) for the week-by-week build plan.

---

## Architecture

```
JSON Server (Mock CRM)
    → FastAPI Integration Layer          (schema validation on ingestion)
        → SQLite                         (normalised unified dataset)
            → ML Engine  +  AI Engine     (scikit-learn/PyCaret + Gemini 2.5 Flash)
                → React Sales Portal      (Azure Static Web Apps + App Service F1)
```

**Four integrated layers:**

| Layer | Responsibility | Key Tech |
|---|---|---|
| 1. CRM Data Integration | Ingest & validate 3 CRM domains (pipeline, account health, rep performance) | FastAPI, JSON Server, SQLite |
| 2. Sales Portal | 4-screen operations UI | React, Recharts, Azure |
| 3. ML Analytics Engine | Revenue forecast, win scoring, health classification | scikit-learn, PyCaret, MLflow |
| 4. AI Sales Intelligence | Scenario-based sales narratives | Google Gemini 2.5 Flash |

---

## Portal Screens

1. **Pipeline Overview** — funnel, weighted forecast, deal list
2. **Account Detail** — account health score, engagement trend, ticket volume
3. **Rep Performance** — win rates, quota attainment, activity
4. **AI Intelligence** — Gemini narratives for Strong / At-Risk / Recovery scenarios

---

## ML Models & Targets

| Model | Algorithm (PyCaret auto-select) | Target |
|---|---|---|
| Revenue Forecaster | Linear Regression / Gradient Boosting | MAPE < 15% |
| Win Probability Scorer | Logistic Regression / Random Forest | AUC-ROC > 0.75 |
| Account Health Classifier | Decision Tree / Gradient Boosting | F1 > 0.75 |

All experiments, params, metrics, and `.pkl` artifacts are tracked in **MLflow**.

---

## Repository Layout

```
SalesIQ/
├── backend/            FastAPI integration layer, ML engine, AI engine
├── frontend/           React 4-screen sales portal
├── data/               JSON Server mock CRM, Faker generators, SQLite db
├── docs/               RFP proposal + reference documents
├── Screenshots/        Demo & evidence captures
├── Solution_proposal.md
├── Implementation.md   Weekly build plan
├── README.md
└── CLAUDE.md           Guidance for Claude Code
```

---

## Getting Started

> Prerequisites: **Python 3.11+**, **Node.js 18+**, **npm**, and (optionally) **Ollama** for offline LLM dev.

### 1. Mock CRM (JSON Server)
```bash
cd data
npm install -g json-server
json-server --watch crm_db.json --port 3001
```

### 2. Backend (FastAPI + ML + AI)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Set the Gemini key before starting: `setx GEMINI_API_KEY "<your-key>"` (new shell required).

### 3. Frontend (React portal)
```bash
cd frontend
npm install
npm run dev
```

### 4. Generate synthetic data (500+ records)
```bash
cd data
python generate_data.py
```

### One-command pipeline (ingest → train → score → sample narrative)
For a fast local setup or demo, run the whole Phase-1 pipeline end to end:
```bash
cd backend
python pipeline_cli.py          # falls back to data/crm_db.json if JSON Server is down
```

> **Auto-model-selection note:** the approved proposal specifies PyCaret for
> automatic model selection. PyCaret's dependency pins are incompatible with
> Python 3.13, so the same behaviour is implemented directly on scikit-learn
> (train each candidate algorithm named in the proposal, compare on the target
> metric, register the winner). MLflow tracking is unchanged. This deviation is
> disclosed in Section 8 of the mid-term document.

---

## Testing

```bash
cd backend
pytest --cov=app --cov-report=term-missing      # unit + integration, ≥80% target

cd ../frontend
npx playwright test                              # E2E across all 4 screens
```

QA runs automatically in **GitHub Actions CI** on every push to `main`.

---

## Cost Summary

| | |
|---|---|
| Azure Backend Hosting | ₹800 |
| Contingency Buffer | ₹500 |
| Everything else (10 of 12 tools) | ₹0 (open-source / free tier) |
| **Total estimated** | **₹1,300** |
| Budget ceiling | ₹2,500 |
| Buffer remaining | ₹1,200 |

---

*L&D Team · Confidential · SalesIQ — S4-I-21 · pSiddhi-2026-01*
