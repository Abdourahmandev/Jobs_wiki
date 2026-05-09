from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from ingestion.un.normalize import normalize_job
from ingestion.un.quality import summarize_quality
from ingestion.un.raw_store import write_raw_payload

_FIELDNAMES = [
    "source",
    "source_job_id",
    "title",
    "organization",
    "location",
    "country",
    "remote_flag",
    "contract_type",
    "grade",
    "posted_at",
    "closes_at",
    "url",
    "description_text",
    "language",
    "ingested_at",
    "run_id",
]


def run_pipeline(
    base_dir: Path,
    run_date: str,
    run_id: str,
    ingested_at: str,
    fetch_payload: Callable[[], dict[str, Any]],
) -> dict[str, Path]:
    payload = fetch_payload()
    raw_path = write_raw_payload(
        base_dir=base_dir,
        run_date=run_date,
        run_id=run_id,
        payload=payload,
    )

    rows = [
        normalize_job(job, run_id=run_id, ingested_at=ingested_at)
        for job in payload.get("data", [])
    ]

    silver_dir = base_dir / "silver" / "reliefweb" / run_date
    silver_dir.mkdir(parents=True, exist_ok=True)
    silver_path = silver_dir / f"{run_id}.csv"

    fieldnames = list(rows[0].keys()) if rows else _FIELDNAMES
    with silver_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize_quality(rows)
    summary_dir = base_dir / "runs" / "reliefweb" / run_date
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / f"{run_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {
        "raw_path": raw_path,
        "silver_path": silver_path,
        "summary_path": summary_path,
    }
