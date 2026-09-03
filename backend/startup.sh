#!/bin/bash
# Azure App Service Linux Custom Startup Script
set -e

echo "Starting SalesIQ FastAPI Service on Azure App Service..."

# Ensure python path includes current directory
export PYTHONPATH=.

# Start uvicorn server
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
