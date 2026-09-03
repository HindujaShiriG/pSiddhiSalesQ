# SalesIQ — Weekly Implementation Plan

> **Project:** S4-I-21 — Unified Sales Operations System
> **Effort:** ~140 hours across 12 active weeks (~11.5 hrs/week)
> **Milestones:** Week 9 (mid-term partial to Moodle) · Week 16 (final complete) · Week 17 (final review)
> QA is embedded in **every** development week. Source of truth: [Solution_proposal.md](Solution_proposal.md).

---

## Phase overview

| Phase | Weeks | Theme |
|---|---|---|
| **Phase 1** | 4–9 | Data layer + portal foundation + initial AI |
| *(gap)* | 10 | Mid-term buffer / review feedback |
| **Phase 2** | 11–16 | Full portal + all AI scenarios + QA hardening |
| **Review** | 17 | Final demo & sign-off |

---

## Phase 1 — Weeks 4–9: Data Layer + Portal Foundation + Initial AI

### Week 4 — Data foundation
- **Build:** Stand up JSON Server as the mock CRM. Design the unified schema for
  pipeline, account, and rep domains. Scaffold the FastAPI service.
- **Deliverable:** Mock CRM running + schema defined.
- **QA:** Schema validation unit tests.
- **Definition of done:** JSON Server serves 3 domain endpoints; FastAPI boots; schema documented.

### Week 5 — First two domains flowing
- **Build:** FastAPI integration for the **pipeline** and **rep performance** domains.
  Persist normalised records into SQLite.
- **Deliverable:** 2 data domains flowing into SQLite.
- **QA:** Integration tests per domain (FastAPI → SQLite).
- **Definition of done:** Pipeline + rep data ingested, validated, and queryable.

### Week 6 — Unified dataset complete
- **Build:** Integrate the **account health** domain. All 3 domains live. Complete
  data normalisation across the unified dataset.
- **Deliverable:** Unified dataset queryable.
- **QA:** Data integrity + completeness tests; invalid records excluded from ML path.
- **Definition of done:** All 3 domains normalised into one queryable dataset.

### Week 7 — First portal screens
- **Build:** React portal — **Pipeline Overview** + **Account Detail** screens.
  Wire the corresponding FastAPI endpoints.
- **Deliverable:** 2 portal screens live, API routing active.
- **QA:** API endpoint schema + response tests.
- **Definition of done:** Two screens render live data from the API.

### Week 8 — First ML models
- **Build:** Train the **Revenue Forecaster** and **Win Probability Scorer** (PyCaret
  auto-select). Set up MLflow experiment tracking.
- **Deliverable:** 2 ML models trained + MLflow logs.
- **QA:** Model accuracy + prediction-range tests.
- **Definition of done:** Both models logged in MLflow, hitting accuracy targets on synthetic data.

### Week 9 — Mid-term milestone 🏁
- **Build:** Mid-term prep. Connect the Gemini API. Generate the initial AI narrative
  for **one** scenario.
- **Deliverable:** Mid-term deliverable complete → **uploaded to Moodle (partial)**.
- **QA:** All Phase 1 tests passing.
- **Definition of done:** End-to-end slice demoable: data → ML → 2 screens → 1 AI narrative.

---

## Week 10 — Buffer
Absorb mid-term feedback, pay down tech debt, and stabilise Phase 1 before scaling up.
No new scope committed here by design.

---

## Phase 2 — Weeks 11–16: Full Portal + All AI + QA

### Week 11 — Portal & ML complete
- **Build:** Add **Rep Performance** + **AI Intelligence** screens. Train the
  **Account Health Classifier** (third ML model).
- **Deliverable:** 4-screen portal complete; all 3 ML models done.
- **QA:** E2E portal screen tests (Playwright).
- **Definition of done:** All four screens live; all three models tracked in MLflow.

### Week 12 — All AI scenarios
- **Build:** Implement all 3 Gemini scenarios — **Strong Quarter**, **At-Risk Quarter**,
  **Recovery** — rendered on the AI Intelligence screen.
- **Deliverable:** All 3 AI narratives live on portal.
- **QA:** Narrative accuracy + coherence tests (scenario-appropriate language, deal/account references).
- **Definition of done:** Each scenario produces a correct, cached, on-portal narrative.

### Week 13 — Azure deployment
- **Build:** End-to-end deployment on Azure (Static Web Apps + App Service F1).
  Configure GitHub Actions CI/CD.
- **Deliverable:** Full system deployed on Azure.
- **QA:** Azure deployment + CI pipeline tests.
- **Definition of done:** Public deploy reachable; CI green on push to `main`.

### Week 14 — QA suite & coverage
- **Build:** Full QA suite run. Generate pytest-cov coverage report. Fix bugs surfaced.
- **Deliverable:** Coverage report generated.
- **QA:** All unit + integration tests passing.
- **Definition of done:** Coverage measured and trending toward ≥80%.

### Week 15 — E2E & quality gate
- **Build:** E2E Playwright tests across all screens. AI quality assertions. Confirm
  **≥80% coverage**.
- **Deliverable:** QA suite complete, coverage ≥ 80%.
- **QA:** Full regression run + QA report.
- **Definition of done:** Coverage gate met; regression suite green.

### Week 16 — Final milestone 🏁
- **Build:** Final documentation (architecture diagram, data flow, test results, ML
  benchmarks, user guide). Demo prep. Full regression.
- **Deliverable:** Final review ready → **uploaded to Moodle (complete)**.
- **QA:** Full regression suite passing.
- **Definition of done:** All acceptance criteria met; demo rehearsed.

---

## Week 17 — Final Review 🎓
Live demonstration:
- Live 3-domain data integration → SQLite with schema validation passing.
- 4-screen portal on Azure, each screen loading < 3s.
- 3 ML models hitting targets (MAPE < 15%, AUC-ROC > 0.75, F1 > 0.75), tracked in MLflow.
- All 3 Gemini scenarios live on the AI Intelligence screen.
- QA suite ≥80% coverage, green in GitHub Actions CI.
- Complete documentation package.

---

## Acceptance criteria checklist

- [x] 3 CRM domains ingested & validated into SQLite (Pipeline, Accounts, Reps)
- [x] 4 portal screens live (Pipeline Overview, Account Detail, Rep Performance, AI Intelligence)
- [x] Revenue Forecaster — MAPE < 15% (Achieved: 0.0537 / 5.37%)
- [x] Win Probability Scorer — AUC-ROC > 0.75 (Achieved: 0.9643)
- [x] Account Health Classifier — F1 > 0.75 (Achieved: 0.7690 - 0.9914)
- [x] All 3 models tracked in MLflow (params, metrics, artifacts logged)
- [x] 3 Gemini scenarios (Strong Quarter / At-Risk Quarter / Recovery) live with grounded fallbacks
- [x] ≥80% test coverage (Achieved: 94% coverage across 34 automated tests)
- [x] Full documentation + Azure deployment guide + Dockerfile + Static Web App config
- [x] Total spend ≤ ₹2,500 (estimated ₹1,300, ₹0 spent in dev)

---

## Risk watch (carry through every week)

| Risk | Mitigation | Fallback |
|---|---|---|
| ML accuracy below target | Faker 500+ records w/ realistic variance; PyCaret auto-select | Document variance in eval report |
| Azure free-tier limits | Budget alert at ₹200; deploy only during demo/test hours | Vercel free tier |
| Gemini rate limits at demo | Pre-generate & cache narratives | Serve cached output |
| FastAPI + SQLite latency | Indexes on hot columns; pre-compute scores at ingestion | `functools.lru_cache` |
| App Service F1 cold start | Health-check ping every 10 min | Pre-warmed Static Functions |

---

*L&D Team · Confidential · SalesIQ — S4-I-21 · pSiddhi-2026-01*
