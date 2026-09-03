# SalesIQ — Azure Deployment Guide (Capstone RFP S4-I-21)

> **Program:** IMPACT pSiddhi 3.0 · Semester 4 — Integration Mastery  
> **Topic ID:** S4-I-21 — Unified Sales Operations System  
> **Budget Ceiling:** ₹2,500 (Fixed Ceiling) · **Estimated Spend:** ₹800–₹1,300  

---

## 1. Cloud Architecture Overview

SalesIQ is deployed end-to-end on Microsoft Azure infrastructure using cloud services optimized for stability, performance, and budget efficiency:

```
[ Client Browser ]
       │
       ▼
[ Azure Static Web Apps (Free Tier) ]  <─── Hosted React + Recharts Portal (4 Screens)
       │ (API Proxy / CORS)
       ▼
[ Azure App Service (F1 Free / Basic Linux ₹800) ]  <─── FastAPI REST API + ML Engine + SQLite
       │
       ├──> [ SQLite Database (Normalised Unified CRM Dataset) ]
       ├──> [ ML Models (.pkl registry: Win Scorer, Revenue Forecaster, Health Classifier) ]
       └──> [ Google Gemini 2.5 Flash / Offline Grounded AI Engine (3 Scenarios) ]
```

---

## 2. Budget Reconciliation & Resource Plan

| Azure Component | Pricing Tier | Purpose | Cost/Semester | Justification |
|---|---|---|---|---|
| **Azure Static Web Apps** | Free Tier (`Free_F1`) | Hosts the 4-screen React portal with global CDN & SSL | **₹0** | Free tier includes 100 GB bandwidth & custom domains |
| **Azure App Service (Linux)** | F1 Free Tier / B1 Basic | Runs the Python FastAPI container/service | **₹800 (max)** | Free tier during dev; paid tier provides dedicated compute |
| **Azure Container Registry / Blob** | Standard (Optional) | Docker image caching | **₹0** (within free credits) | Direct Git/zip deploy preferred to save costs |
| **Google AI Studio (Gemini)** | Free Tier | Primary AI narrative generation | **₹0** | Free tier covers all demo & development quotas |
| **Contingency Reserve** | — | Compute overage buffer | **₹500** | Reserved for unexpected spikes |
| **Total Estimated Spend** | — | **Full End-to-End System** | **₹1,300** | **₹1,200 remaining under the ₹2,500 ceiling** |

---

## 3. Step-by-Step Deployment Guide

### A. Frontend: Azure Static Web Apps
1. **Build the production bundle**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. **Deploy via Azure CLI or GitHub Actions**:
   ```bash
   az staticwebapp create \
     --name salesiq-portal \
     --resource-group salesiq-rg \
     --source https://github.com/HindujaShiriG/pSiddhiSalesQ \
     --location "eastus2" \
     --branch "main" \
     --app-location "/frontend" \
     --output-location "dist"
   ```
   *The included `staticwebapp.config.json` automatically configures SPA routing and API fallbacks.*

### B. Backend: Azure App Service (Linux)
1. **Create the App Service Plan & Web App**:
   ```bash
   az appservice plan create \
     --name salesiq-plan \
     --resource-group salesiq-rg \
     --sku F1 \
     --is-linux

   az webapp create \
     --resource-group salesiq-rg \
     --plan salesiq-plan \
     --name salesiq-api \
     --runtime "PYTHON:3.12"
   ```
2. **Configure App Settings**:
   ```bash
   az webapp config appsettings set \
     --resource-group salesiq-rg \
     --name salesiq-api \
     --settings \
       WEBSITES_PORT="8000" \
       GEMINI_API_KEY="<YOUR_GEMINI_KEY>" \
       GEMINI_MODEL="gemini-2.5-flash"
   ```
3. **Deploy the Code**:
   Deploy using the Azure Web App deployment center or Azure CLI zip deployment:
   ```bash
   cd backend
   az webapp up --name salesiq-api --resource-group salesiq-rg
   ```

---

## 4. Verification & Health Check

After deployment, verify that all components operate end-to-end:
1. **Backend Health Check**:
   `GET https://salesiq-api.azurewebsites.net/api/pipeline/overview`
2. **AI Scenarios Verification**:
   `GET https://salesiq-api.azurewebsites.net/api/intelligence/scenarios`
3. **ML Models Verification**:
   `GET https://salesiq-api.azurewebsites.net/api/admin/models`
   *(Confirms all 3 models: `win_scorer`, `revenue_forecaster`, and `health_classifier` are active)*.
4. **Portal Verification**:
   Navigate to `https://salesiq-portal.azurestaticapps.net` and verify all 4 screens render in **< 3 seconds**.
