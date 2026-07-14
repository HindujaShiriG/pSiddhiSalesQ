"""Model training with PyCaret-style auto-select + MLflow experiment tracking.

Auto-select
-----------
The approved proposal specifies PyCaret for automatic model selection. PyCaret's
strict dependency pins are not compatible with Python 3.13, so we implement the
same behaviour directly on scikit-learn: train several candidate algorithms with
cross-validation, compare them on the target metric, and register the winner.
This deviation is disclosed in Section 8 of the mid-term document. The candidate
algorithms are exactly those named in the proposal.

Two Phase-1 models are trained here:
  * revenue_forecaster — regression   (target: MAPE < 15%)
  * win_scorer         — classification (target: AUC-ROC > 0.75)

The account-health classifier is a Phase-2 (Week-11) deliverable and is not
trained yet.

MLflow logs parameters, metrics, and the winning model for every run. Tracking
uses a local file store (no server required); failures degrade gracefully so
training never hard-fails on an MLflow issue.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_percentage_error, roc_auc_score
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy.orm import Session

from ..config import settings
from . import features, registry

logger = logging.getLogger("salesiq.ml")

try:
    import mlflow

    _MLFLOW = True
except Exception:  # pragma: no cover - optional dependency
    _MLFLOW = False


@contextmanager
def _mlflow_run(run_name: str, params: dict):
    """Best-effort MLflow run; a no-op if MLflow is unavailable/misconfigured."""
    if not _MLFLOW:
        yield None
        return
    try:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(params)
            yield mlflow
    except Exception as exc:  # pragma: no cover
        logger.warning("MLflow disabled for this run: %s", exc)
        yield None


def _preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )


def _cv_folds(n_samples: int, want: int = 5) -> int:
    """Clamp CV folds so tiny synthetic subsets don't crash cross-validation."""
    return max(2, min(want, n_samples // 3)) if n_samples >= 6 else 2


# --------------------------------------------------------------------------- #
# Win-probability scorer (classification)
# --------------------------------------------------------------------------- #
def train_win_scorer(session: Session) -> dict:
    df = features.build_deal_frame(session)
    X, y = features.win_training_frame(df)
    if len(y) < 10 or y.nunique() < 2:
        raise ValueError("insufficient labelled deals to train win scorer")

    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
    }
    folds = _cv_folds(len(y))
    prep = lambda: _preprocessor(features.WIN_NUMERIC, features.WIN_CATEGORICAL)
    results = {}
    for name, clf in candidates.items():
        pipe = Pipeline([("prep", prep()), ("model", clf)])
        auc = cross_val_score(pipe, X, y, cv=folds, scoring="roc_auc").mean()
        results[name] = float(auc)
        logger.info("win_scorer candidate %s: AUC=%.3f", name, auc)

    best_name = max(results, key=results.get)
    best_auc = results[best_name]
    best_pipe = Pipeline([("prep", prep()), ("model", candidates[best_name])])
    best_pipe.fit(X, y)

    meta = {
        "model": "win_scorer",
        "algorithm": best_name,
        "metric": "AUC-ROC",
        "metric_value": round(best_auc, 4),
        "target": 0.75,
        "meets_target": best_auc > 0.75,
        "candidates": {k: round(v, 4) for k, v in results.items()},
        "n_train": int(len(y)),
        "features": features.WIN_FEATURES,
    }
    with _mlflow_run("win_scorer", {"algorithm": best_name, "cv_folds": folds}) as mf:
        if mf:
            mf.log_metric("auc_roc", best_auc)
            for k, v in results.items():
                mf.log_metric(f"cv_auc_{k}", v)
    registry.save_model("win_scorer", best_pipe, meta)
    logger.info("win_scorer trained: %s AUC=%.3f (target>0.75: %s)",
                best_name, best_auc, meta["meets_target"])
    return meta


# --------------------------------------------------------------------------- #
# Revenue forecaster (regression)
# --------------------------------------------------------------------------- #
def train_revenue_forecaster(session: Session) -> dict:
    df = features.build_deal_frame(session)
    X, y = features.revenue_training_frame(df)
    if len(y) < 10:
        raise ValueError("insufficient closed-won deals to train revenue forecaster")

    candidates = {
        "LinearRegression": LinearRegression(),
        "GradientBoosting": GradientBoostingRegressor(random_state=42),
    }
    folds = _cv_folds(len(y))
    prep = lambda: _preprocessor(features.REVENUE_NUMERIC, features.REVENUE_CATEGORICAL)
    results = {}
    for name, reg in candidates.items():
        pipe = Pipeline([("prep", prep()), ("model", reg)])
        preds = cross_val_predict(pipe, X, y, cv=folds)
        mape = float(mean_absolute_percentage_error(y, preds))
        results[name] = mape
        logger.info("revenue_forecaster candidate %s: MAPE=%.3f", name, mape)

    best_name = min(results, key=results.get)  # lower MAPE is better
    best_mape = results[best_name]
    best_pipe = Pipeline([("prep", prep()), ("model", candidates[best_name])])
    best_pipe.fit(X, y)

    meta = {
        "model": "revenue_forecaster",
        "algorithm": best_name,
        "metric": "MAPE",
        "metric_value": round(best_mape, 4),
        "target": 0.15,
        "meets_target": best_mape < 0.15,
        "candidates": {k: round(v, 4) for k, v in results.items()},
        "n_train": int(len(y)),
        "features": features.REVENUE_FEATURES,
    }
    with _mlflow_run("revenue_forecaster", {"algorithm": best_name, "cv_folds": folds}) as mf:
        if mf:
            mf.log_metric("mape", best_mape)
            for k, v in results.items():
                mf.log_metric(f"cv_mape_{k}", v)
    registry.save_model("revenue_forecaster", best_pipe, meta)
    logger.info("revenue_forecaster trained: %s MAPE=%.3f (target<0.15: %s)",
                best_name, best_mape, meta["meets_target"])
    return meta


def train_all(session: Session) -> dict:
    """Train both Phase-1 models and return their metadata."""
    return {
        "win_scorer": train_win_scorer(session),
        "revenue_forecaster": train_revenue_forecaster(session),
    }
