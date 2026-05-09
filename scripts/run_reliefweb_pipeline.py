from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import requests

from ingestion.un.pipeline import run_pipeline
from ingestion.un.reliefweb_client import RELIEFWEB_APP_NAME, RELIEFWEB_JOBS_URL, build_jobs_request


def fetch_payload() -> dict:
    response = requests.post(
        RELIEFWEB_JOBS_URL,
        params={"appname": RELIEFWEB_APP_NAME},
        json=build_jobs_request(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    now = datetime.now(UTC)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    result = run_pipeline(
        base_dir=Path("data"),
        run_date=now.strftime("%Y-%m-%d"),
        run_id=run_id,
        ingested_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        fetch_payload=fetch_payload,
    )
    print(f"ReliefWeb pipeline completed for run {run_id}")
    print(f"  raw:     {result['raw_path']}")
    print(f"  silver:  {result['silver_path']}")
    print(f"  summary: {result['summary_path']}")
