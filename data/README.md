# SalesIQ — Data Layer (Mock CRM)

Synthetic CRM data + JSON Server mock, feeding the FastAPI integration layer.

## Domains

| Collection | Records (default) | Purpose |
|---|---|---|
| `pipeline` | 420 deals | Opportunities with stage, amount, age, win label |
| `accounts` | 120 accounts | Account-health signals (engagement, tickets, renewal) |
| `reps` | 40 reps | Rep performance (win rate, quota attainment, activity) |

Total ≈ **580 records** (proposal target: 500+).

## Generate data

```bash
python generate_data.py                      # writes crm_db.json (seeded, reproducible)
python generate_data.py --deals 500          # override counts
```

A small fraction of deals (`--drop-rate`, default 3%) are emitted with a missing
required field on purpose, so the backend's schema-validation layer has invalid
records to reject (Week-4 QA).

## Serve as REST (JSON Server)

```bash
npm install
npm run crm                                  # http://localhost:3001/pipeline | /accounts | /reps
```

The backend reads `CRM_BASE_URL` (default `http://localhost:3001`). If the server
isn't running, ingestion falls back to reading `crm_db.json` directly.
