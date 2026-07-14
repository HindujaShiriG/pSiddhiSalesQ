"""Model registry — persist/load trained pipelines as .pkl artifacts.

Metadata (metric, algorithm, trained-at proxy) is stored alongside each model so
the API and QA can report which algorithm PyCaret-style auto-select picked.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

from ..config import settings

MODEL_DIR = Path(settings.model_dir)


def _paths(name: str) -> tuple[Path, Path]:
    return MODEL_DIR / f"{name}.pkl", MODEL_DIR / f"{name}.meta.json"


def save_model(name: str, model: Any, meta: dict) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path, meta_path = _paths(name)
    joblib.dump(model, model_path)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return model_path


def load_model(name: str) -> tuple[Any, dict]:
    model_path, meta_path = _paths(name)
    if not model_path.exists():
        raise FileNotFoundError(f"model {name!r} not trained yet ({model_path})")
    model = joblib.load(model_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    return model, meta


def model_exists(name: str) -> bool:
    return _paths(name)[0].exists()
