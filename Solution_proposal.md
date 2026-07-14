# SalesIQ — Solution Proposal

> **Reference document** distilled from `docs/SalesIQ_RFP_Proposal_S4-I-21_Hindujashiri_P403 (5).docx`
> **Program:** IMPACT pSiddhi · Semester 4 — Integration Mastery (Capstone) · `pSiddhi-2026-01`
> **RFP Response:** S4-I-21 — Unified Sales Operations System
> **Budget:** ₹2,500 fixed ceiling · QA mandatory · AI core

---

## 1. Topic & Participant

| Field | Value |
|---|---|
| Topic ID | S4-I-21 |
| Topic Title | Unified Sales Operations System |
| Full Name | Hindujashiri Gopu |
| Employee ID | P403 |
| Semester | 4 — Integration Mastery (Capstone) |
| History | Completed 3 semesters in different models; starting the AI Core Model in the 4th semester |

---

## 2. Problem Understanding

The sales function operates across **four interlocked failure modes** that compound one another. Managers make high-stakes pipeline decisions from data that is stale, subjectively weighted, and structurally incomplete.

1. **CRM Data Integrity Failure → Blind Pipeline Decisions.** Pipeline stages, deal values, close dates, and contacts are updated sporadically — days or weeks late. Managers commit resources and forecast revenue against data that no longer reflects reality: lost deals appear open, disengaged accounts appear healthy.

2. **Structural Forecast Inaccuracy from Stage-Weighted Methodology.** Fixed stage weights (Proposal 50%, Negotiation 75%) treat all deals in a stage as equivalent. A deal at Negotiation with a 30%-win-rate rep differs materially from one with an 80% rep; a 45-day-stalled deal differs from a 3-day-old one. This produces systematically inaccurate forecasts.

3. **Invisible Account Health Signals → Predictable Churn.** Declining engagement, rising ticket volume, stalling expansion, and lengthening response times are measurable leading indicators 3–6 months before renewal. Without continuous monitoring, none surface until the customer is already in exit conversations.

4. **Absent AI/ML Intelligence Across the Sales Cycle.** Without ML, deal prioritisation defaults to intuition, forecasting to stage percentages, and retention to reactive escalation — lowering win rates, damaging forecast credibility, and losing preventable customers.

---

## 3. Proposed Solution

**SalesIQ** — a unified, AI-powered sales operations system with **four integrated layers**, each eliminating one failure mode. Built entirely within the ₹2,500 budget using Azure and open-source tools.

### Layer 1 — Unified CRM Data Integration Layer
- Ingests pipeline, account health, and rep performance data across **3 domains** via a Python **FastAPI** service.
- **JSON Server** simulates the mock CRM — REST endpoints for all three domains at zero cost.
- **SQLite** stores the normalised unified dataset, queryable by the ML engine and React portal.
- **Schema validation** on ingestion — records with missing required fields are logged and excluded from ML inference.

### Layer 2 — Sales Portal on Azure (4 Screens)
- **React** frontend on **Azure Static Web Apps** (Free tier).
- **FastAPI** backend on **Azure App Service F1 (Linux)**.
- 4 functional screens: **Pipeline Overview, Account Detail, Rep Performance, AI Intelligence**.
- Azure Functions-style triggers handle background ML inference and data refresh.

### Layer 3 — ML Analytics Engine
- **Revenue Forecaster:** Linear Regression / Gradient Boosting (PyCaret auto-select) — **MAPE target < 15%**.
- **Win Probability Scorer:** Logistic Regression / Random Forest (PyCaret auto-select) — **AUC-ROC target > 0.75**.
- **Account Health Classifier:** Decision Tree / Gradient Boosting (PyCaret auto-select) — **F1 target > 0.75**.
- **MLflow** tracks experiments, logs params/metrics, and stores `.pkl` artifacts.

### Layer 4 — AI Sales Intelligence Engine (AI Core)
- **Google AI Studio — Gemini 2.5 Flash** (Free Tier) generates scenario-based narratives.
- **Strong Quarter:** momentum tactics, upsell identification, stretch targets.
- **At-Risk Quarter:** risk mitigation, deal acceleration, account retention.
- **Recovery Scenario:** priority deal ranking, rep coaching focus, account recovery plays.
- Covers all **3 required AI scenarios** — AI is the operational core, not a cosmetic label.

### Architecture Flow
```
JSON Server (Mock CRM)
    → FastAPI Integration Layer
        → SQLite
            → [ scikit-learn / PyCaret ML Models  +  Gemini AI Narratives ]
                → React Sales Portal (Azure Static Web Apps + App Service)
```

---

## 4. Tools, Subscriptions & Cost Breakdown

| Tool / Service | Purpose | Tier | Cost/Sem | Justification |
|---|---|---|---|---|
| ✅ Azure Backend Hosting | Portal frontend + backend stability hosting | Paid | ₹800 | Production-grade uptime & backend performance |
| Azure App Service F1 (Linux) | FastAPI backend hosting | Free | ₹0 | F1 free tier |
| Python FastAPI + SQLite | Integration layer + data persistence | Open source | ₹0 | Single Python runtime |
| JSON Server | Mock CRM REST endpoints (3 domains) | Open source | ₹0 | Zero cost, instant setup |
| scikit-learn + PyCaret + MLflow | ML forecast, scoring, classification | Free | ₹0 | All open-source |
| Google AI Studio — Gemini 2.5 Flash | AI scenario narratives | Free tier | ₹0 | Free tier covers semester usage |
| React + Recharts | 4-screen portal + charts | Free | ₹0 | Open-source component library |
| Ollama + Llama 4 Scout (8B) | Local LLM for offline dev | Free | ₹0 | Runs locally |
| GitHub (free tier) | Version control + CI/CD | Free | ₹0 | 2,000 Actions min/month free |
| pytest + pytest-cov + Playwright + httpx | QA test suite — all layers | Free | ₹0 | Open-source testing frameworks |
| Faker (Python) | Synthetic CRM data (500+ records) | Free | ₹0 | Open-source |
| Contingency Buffer | Unexpected API/compute overages | — | ₹500 | Reserved for overages |

**Total estimated cost: ₹1,300 / semester** · Budget ceiling: ₹2,500 · **Buffer remaining: ₹1,200**

> **Budget efficiency:** 10 of 12 tools are FREE (open-source or free tier). Azure Backend Hosting (₹800) ensures stability; contingency buffer (₹500) covers overages.

---

## 5. Timeline & Effort

### Phase 1 — Weeks 4–9: Data Layer + Portal Foundation + Initial AI

| Week | Task | Deliverable | QA Activity |
|---|---|---|---|
| Wk 4 | JSON Server setup; unified schema design; FastAPI scaffold | Mock CRM running + schema defined | Schema validation unit tests |
| Wk 5 | FastAPI integration for pipeline + rep domains; SQLite persistence | 2 domains flowing into SQLite | Integration tests per domain |
| Wk 6 | Account health domain; all 3 domains live; normalisation complete | Unified dataset queryable | Data integrity + completeness tests |
| Wk 7 | React portal: Pipeline Overview + Account Detail; FastAPI endpoints | 2 screens live, API routing active | API endpoint schema + response tests |
| Wk 8 | ML: Revenue Forecaster + Win Probability Scorer; MLflow tracking | 2 ML models trained + MLflow logs | Model accuracy + range tests |
| Wk 9 | Mid-term prep; Gemini connected; initial AI narrative (1 scenario) | Mid-term deliverable complete | All Phase 1 tests passing |

### Phase 2 — Weeks 11–16: Full Portal + All AI + QA

| Week | Task | Deliverable | QA Activity |
|---|---|---|---|
| Wk 11 | Rep Performance + AI Intelligence screens; Account Health Classifier | 4-screen portal complete; all 3 ML models | E2E portal tests (Playwright) |
| Wk 12 | All 3 Gemini scenarios: Strong, At-Risk, Recovery | All 3 narratives live on portal | Narrative accuracy + coherence tests |
| Wk 13 | Azure end-to-end deployment; GitHub Actions CI/CD | Full system deployed on Azure | Azure deployment + CI pipeline tests |
| Wk 14 | Full QA suite; pytest-cov coverage report; bug fixes | Coverage report generated | All unit + integration tests passing |
| Wk 15 | E2E Playwright tests; AI quality assertions; 80% coverage | QA suite complete, coverage ≥ 80% | Full regression + QA report |
| Wk 16 | Final docs; demo prep; full regression; upload to Moodle | Final review ready | Full regression suite passing |

> **Total effort:** ~140 hours across 12 weeks (~11.5 hrs/week). QA embedded in every development week.

---

## 6. Tech Stack

| Layer | Technologies | Cost |
|---|---|---|
| Language | Python (FastAPI, ML, data), JavaScript/React (frontend) | Free |
| AI/ML Models | scikit-learn, PyCaret (auto model selection), MLflow (tracking) | Free |
| AI API (narratives only) | Gemini 2.5 Flash — scenario narratives & commentary only | ₹0 (free tier) |
| Database | SQLite (embedded, zero-config) | Free |
| Mock CRM | JSON Server — REST endpoints for 3 CRM domains | Free |
| Cloud Hosting | Azure Static Web Apps Free + Azure App Service F1 (Linux) | ₹800 |
| Portal / Charts | React + Recharts (funnel, gauges, bar, trend lines) | Free |
| Data Generation | Faker (Python) — 500+ synthetic CRM records | Free |
| QA Framework | pytest + pytest-cov + Playwright + httpx + GitHub Actions CI | Free |
| Version Control | Git + GitHub | Free |

> Python is the primary development language for backend, ML, and data processing.

---

## 7. Expected Deliverable / POC (Week 17 Final Review)

- Live data integration across all 3 CRM domains via FastAPI into SQLite, with schema validation passing.
- Fully functional **4-screen SalesIQ portal** on Azure Static Web Apps, all screens loading in **under 3 seconds**.
- **3 trained ML models** with validated accuracy — Revenue Forecaster (MAPE < 15%), Win Probability Scorer (AUC-ROC > 0.75), Account Health Classifier (F1 > 0.75) — all tracked in MLflow.
- AI-generated narratives via Gemini 2.5 Flash across all 3 scenarios, displayed live on the AI Intelligence screen.
- QA test suite with **≥80% coverage** across integration, ML, portal, and AI layers — passing in GitHub Actions CI.
- Complete documentation: architecture diagram, data flow, test results, ML benchmarks, and user guide.
- Evidence uploaded to Moodle at **Week 9** (mid-term partial) and **Week 16** (final complete).

---

## 8. QA Strategy (Mandatory)

### 8.1 Approach
Multi-layered testing covering every component — CRM integration pipeline, ML inference, React screens, FastAPI endpoints, and AI narrative chain. QA is embedded into every development week, not added at the end. GitHub Actions CI runs all tests on every push to `main`.

### 8.2 Test Types & Coverage

| Test Type | Covers | Tool | Target |
|---|---|---|---|
| Unit | ML prediction ranges, endpoint logic, normalisation functions | pytest | >80% coverage |
| Integration | FastAPI → SQLite flows, all 3 domain ingestion pipelines | pytest + httpx | All 3 domains |
| E2E | Full pipeline: JSON Server → FastAPI → ML → screens → AI narrative | Playwright | All 4 screens |
| ML Accuracy | Forecast MAPE, win AUC-ROC, health F1 | scikit-learn metrics | All 3 targets met |
| AI Quality | Narratives contain scenario-appropriate language & deal/account refs | pytest + string matching | All 3 scenarios |
| Data Validation | Schema completeness, field types, referential integrity | pytest fixtures | Zero invalid records to ML |
| Regression | All tests on every push | GitHub Actions CI | 100% pass on merge |

### 8.3 AI-Assisted QA
- Use Gemini to generate synthetic edge-case CRM datasets — zero-activity reps, 100%-ticket/zero-engagement accounts, 60+ day stalled deals.
- Automated anomaly detection on ML outputs — flag predictions deviating from baseline distribution between runs.
- Use AI to review AI-generated narratives for factual consistency against underlying ML scores and pipeline state.

### 8.4 QA Deliverables
- pytest suite with >80% coverage on GitHub.
- GitHub Actions CI pipeline running all tests on every push to `main`.
- QA Report with coverage metrics, ML benchmarks, screen test evidence, and AI narrative quality scores.
- Evidence uploaded to Moodle at Week 9 (partial) and Week 16 (complete).

---

## 9. Risks & Mitigations

| # | Risk | Impact | Mitigation | Fallback |
|---|---|---|---|---|
| 1 | ML accuracy below target on synthetic data | Model unreliable | Faker 500+ records with realistic variance; PyCaret auto-selects best model | Document variance in model evaluation report |
| 2 | Azure free tier limits exceeded | Unexpected costs | Budget alert at ₹200; deploy only during active demo/testing | Deploy portal on Vercel free tier |
| 3 | Gemini API rate limits during demo | AI narratives not live | Pre-generate & cache narratives before demo | Display cached outputs with generation note |
| 4 | FastAPI + SQLite performance insufficient | Slow portal loads | SQLite indexes on key columns; pre-compute ML scores at ingestion | In-memory caching (`functools.lru_cache`) |
| 5 | Azure App Service F1 cold starts | Slow first-load | Health-check ping every 10 min to keep instance warm | Azure Static Functions with pre-warmed handlers |

---

## 10. Semester Alignment (S4 — Integration Mastery)

- **Full-stack, end-to-end platform** — not a single-feature tool — integrating CRM data processing, a REST API integration layer, ML analytics, AI narrative generation, and a 4-screen React portal.
- **AI/ML is the core engine** driving win scoring, revenue forecasting, and health classification — three dedicated models for three distinct problems.
- Covers the **complete sales data lifecycle**: fragmented CRM sources → unified integration → ML inference → AI narration → React portal → Azure deployment.
- **Azure deployment + FastAPI integration** demonstrate the integration mastery expected at Semester 4.
- **QA embedded throughout** with ≥80% coverage across all four layers, measured by pytest-cov and reported in GitHub Actions CI.
- **Budget efficiently managed** at ₹1,300 estimated spend against the ₹2,500 ceiling — ₹1,200 buffer.

---

*L&D Team · Confidential · SalesIQ — S4-I-21 Proposal · pSiddhi-2026-01*
