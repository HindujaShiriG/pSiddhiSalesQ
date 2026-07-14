# SalesIQ Portal (Frontend)

React + Vite + Recharts. Phase 1 screens: **Pipeline Overview** and **Account Detail**.
Rep Performance and AI Intelligence screens land in Phase 2 (Weeks 11–12).

## Run

```bash
npm install
npm run dev            # http://localhost:5173  (proxies /api -> http://localhost:8000)
```

Set `VITE_API_TARGET` (see `.env.example`) if the backend runs elsewhere.

## Build

```bash
npm run build          # outputs dist/
npm run preview
```

The **↻ Refresh data + ML** button on Pipeline Overview triggers the backend
ingest → train → score pipeline, then reloads the view.
