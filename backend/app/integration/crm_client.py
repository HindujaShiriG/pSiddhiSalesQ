"""CRM source client.

Primary source is the JSON Server mock CRM (REST). If it is not reachable, we
fall back to reading the generated ``crm_db.json`` directly — so the integration
pipeline runs end-to-end in CI and offline dev without requiring the node
process to be up. The fallback is logged, never silent.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from ..config import settings

logger = logging.getLogger("salesiq.integration")

DOMAINS = ("pipeline", "accounts", "reps")


class CRMClient:
    def __init__(self, base_url: str | None = None, fallback_file: str | None = None) -> None:
        self.base_url = (base_url or settings.crm_base_url).rstrip("/")
        self.fallback_file = Path(fallback_file or settings.crm_fallback_file)

    def _fetch_http(self, domain: str, timeout: float) -> list[dict]:
        url = f"{self.base_url}/{domain}"
        resp = httpx.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _fetch_file(self, domain: str) -> list[dict]:
        if not self.fallback_file.exists():
            raise FileNotFoundError(
                f"CRM fallback file not found: {self.fallback_file}. "
                f"Run `python data/generate_data.py` first."
            )
        db = json.loads(self.fallback_file.read_text(encoding="utf-8"))
        return db.get(domain, [])

    def fetch(self, domain: str, timeout: float = 3.0) -> list[dict]:
        """Fetch one domain, preferring the live JSON Server, falling back to file."""
        if domain not in DOMAINS:
            raise ValueError(f"unknown domain: {domain!r}")
        try:
            records = self._fetch_http(domain, timeout)
            logger.info("Fetched %d %s records from JSON Server", len(records), domain)
            return records
        except (httpx.HTTPError, OSError) as exc:
            logger.warning(
                "JSON Server unavailable (%s) — falling back to %s for domain %r",
                exc.__class__.__name__, self.fallback_file.name, domain,
            )
            records = self._fetch_file(domain)
            logger.info("Loaded %d %s records from fallback file", len(records), domain)
            return records

    def fetch_all(self, timeout: float = 3.0) -> dict[str, list[dict]]:
        return {d: self.fetch(d, timeout) for d in DOMAINS}
