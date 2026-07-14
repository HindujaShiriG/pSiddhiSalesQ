# SalesIQ — Run Guide & Evidence Capture (Mid-Term)

Step-by-step to run the whole project on your laptop and capture each screenshot
for `pSiddhi3_0_MidTerm_Submission_Template.docx`. Evidence IDs (**EV-01 … EV-08**)
match [MidTerm_Evidence_Map.md](MidTerm_Evidence_Map.md).

> Every command is Windows **PowerShell**, run from the project root
> `C:\Users\hindujashiri.gopu\Documents\SalesIQ` unless stated otherwise.
> Tip: press **Win + Shift + S** to capture a screenshot region on Windows.

---

## 0. Prerequisites (already installed on this laptop)

| Tool | Version needed | Check |
|---|---|---|
| Python | 3.11+ (you have 3.13) | `python --version` |
| Node.js | 18+ (you have 22) | `node --version` |
| npm | 9+ (you have 10) | `npm --version` |

---

## 1. One-time setup

You only do this **once**. Open PowerShell in the project root.

### 1a. Backend virtual environment + dependencies
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```
> If activation is blocked by execution policy, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and retry.

### 1b. Frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

### 1c. (Optional) Mock CRM server dependencies
```powershell
cd data
npm install
cd ..
```

---

## 2. Generate the synthetic CRM data  → 📸 **EV-01**

```powershell
cd data
python generate_data.py
cd ..
```

**Expected output** (screenshot this):
```
Wrote ...\data\crm_db.json
  pipeline (deals): 500  (15 intentionally invalid)
  accounts        : 120
  reps            : 40
  TOTAL records   : 660  (target >= 500: OK)
```
📸 **EV-01** — proves 500+ synthetic records generated with invalid records for
validation. *Deliverable: D-01.*

---

## 3. Run the full data → ML → AI pipeline  → 📸 **EV-02**

This ingests the data, trains both ML models, scores deals, and prints a sample
AI narrative — all in one command.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1        # if not already active
python pipeline_cli.py
cd ..
```

**Expected output** (screenshot this):
```
== Ingesting ==
   accepted=645 rejected=15
   reps     : 40/40 accepted
   accounts : 120/120 accepted
   pipeline : 485/500 accepted
== Training models ==
   win_scorer: LogisticRegression AUC-ROC=0.96 (meets target: True)
   revenue_forecaster: GradientBoosting MAPE=0.05 (meets target: True)
== Scoring deals ==
   {'scored': 485}
== Sample AI narrative (strong_quarter) ==
   source=fallback
   { ...brief... }
```
📸 **EV-02** — proves ingestion (3 domains, invalid rejected), both models trained
and hitting targets, deals scored. *Deliverables: D-02, D-03, D-05.*

> The line `JSON Server unavailable ... falling back to crm_db.json` is **normal**
> here — you haven't started the mock server yet, so it reads the file directly.

---

## 4. Run the QA test suite with coverage  → 📸 **EV-03**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
cd ..
```

**Expected output** (screenshot the summary):
```
............................                     [100%]
---------- coverage: ... ----------
TOTAL                             648     48    93%
28 passed in ~32s
```
📸 **EV-03** — proves ≥80% coverage (you have ~93%) and 28 passing tests across
all layers. *Deliverable: QA (template Section 6).*
> A full HTML report is written to `backend/htmlcov/index.html` — open it in a
> browser for a nicer coverage screenshot if you like.

---

## 5. Start the backend API server (keep this terminal open)

Open **Terminal A**:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --port 8000
```
Wait until you see `Application startup complete.` Leave it running.

### 5a. Interactive API docs  → 📸 **EV-04**
Open a browser to **http://localhost:8000/docs**

Try these endpoints with **"Try it out" → Execute** and screenshot the JSON response:
- `GET /api/pipeline/overview` — note **ml_forecast vs stage_weighted_forecast**
- `GET /api/admin/models` — shows both models' algorithm + AUC/MAPE

📸 **EV-04** — proves the FastAPI layer serves live data and the ML forecast
differs from the naive stage-weighted forecast. *Deliverables: D-04, D-05.*

---

## 6. (Optional but recommended) Start the mock CRM server

This makes the demo show a *live* REST integration instead of the file fallback.

Open **Terminal B**:
```powershell
cd data
npm run crm
```
Runs JSON Server on **http://localhost:3001** (try `/pipeline`, `/accounts`, `/reps`).
With this running, re-hitting `POST /api/admin/ingest` in the docs will show the
`Fetched N records from JSON Server` log instead of the fallback.

---

## 7. Start the React portal (keep this terminal open)

Open **Terminal C**:
```powershell
cd frontend
npm run dev
```
Open the URL it prints — **http://localhost:5173**

### 7a. Pipeline Overview screen  → 📸 **EV-05**
Landing screen. Screenshot the full page showing:
- KPI cards (open deals, pipeline value, stage-weighted forecast, **ML forecast**)
- the stage bar chart (stage-weighted vs ML-weighted)
- the "Top deals by expected revenue" table

📸 **EV-05** — proves Pipeline Overview screen is live and reading the API.
*Deliverable: D-04.*

> If the KPIs show "—", click **↻ Refresh data + ML** once (it runs ingest →
> train → score), then the numbers populate.

### 7b. Account Detail screen  → 📸 **EV-06**
Click **Account Detail** in the sidebar. Pick an account from the dropdown.
Screenshot the health KPIs, the deals table, and the portfolio health pie chart.

📸 **EV-06** — proves Account Detail screen + account-health domain integration.
*Deliverables: D-03, D-04.*

---

## 8. AI narrative  → 📸 **EV-07**

Easiest capture is via the API docs (from step 5a) or a browser:

Open **http://localhost:8000/api/intelligence/narrative?scenario=strong_quarter**

Screenshot the JSON — note `"scenario": "strong_quarter"`, `"source"`, and the
`"narrative"` text grounded in real deal/account figures.

📸 **EV-07** — proves the Week-9 AI intelligence deliverable (Strong Quarter
scenario). *Deliverable: D-06.*

> `"source": "fallback"` means the deterministic offline generator produced it.
> To use real Gemini: set `GEMINI_API_KEY` in `backend/.env` (copy from
> `.env.example`), restart the backend, and `source` becomes `"gemini"`.

---

## 9. MLflow experiment tracking  → 📸 **EV-08**

The training runs are logged to `backend/mlruns/`. To view them in the MLflow UI:

Open **Terminal D**:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
mlflow ui --backend-store-uri ./mlruns --port 5000
```
Open **http://localhost:5000**, click the **salesiq** experiment, and screenshot
the runs showing logged parameters (algorithm) and metrics (auc_roc / mape).

📸 **EV-08** — proves MLflow tracking of model experiments. *Deliverable: D-05.*

---

## Summary — what's running where

| Terminal | Command | URL | Purpose |
|---|---|---|---|
| A | `uvicorn app.main:app --port 8000` | http://localhost:8000/docs | Backend API |
| B *(optional)* | `npm run crm` (in `data/`) | http://localhost:3001 | Mock CRM |
| C | `npm run dev` (in `frontend/`) | http://localhost:5173 | Portal |
| D *(for EV-08)* | `mlflow ui ... --port 5000` | http://localhost:5000 | ML tracking |

## Evidence → deliverable quick reference

| Evidence | Step | Deliverable(s) |
|---|---|---|
| EV-01 data generation | 2 | D-01 |
| EV-02 pipeline (ingest/train/score) | 3 | D-02, D-03, D-05 |
| EV-03 test coverage | 4 | QA (Sec 6) |
| EV-04 API responses | 5a | D-04, D-05 |
| EV-05 Pipeline Overview screen | 7a | D-04 |
| EV-06 Account Detail screen | 7b | D-03, D-04 |
| EV-07 AI narrative | 8 | D-06 |
| EV-08 MLflow runs | 9 | D-05 |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then retry |
| Portal KPIs show "—" | Click **↻ Refresh data + ML** on Pipeline Overview, or run `python pipeline_cli.py` first |
| Portal can't reach API | Make sure the backend (Terminal A) is running on port 8000 |
| `pytest` / `uvicorn` not found | Activate the venv: `.\.venv\Scripts\Activate.ps1` |
| Port already in use | Change the port (e.g. `--port 8001`) or close the other process |
| MLflow shows a Git warning | Harmless — set `$env:GIT_PYTHON_REFRESH="quiet"` to silence |

## Reset to a clean state (optional)
```powershell
cd backend
Remove-Item salesiq.db, models, mlruns, htmlcov, .coverage -Recurse -Force -ErrorAction SilentlyContinue
```
Then re-run from step 2.
