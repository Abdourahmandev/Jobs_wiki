# ReliefWeb Pilot Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python pipeline that fetches ReliefWeb jobs, stores dated raw payloads, produces a canonical silver dataset, and emits a run summary with quality signals.

**Architecture:** Keep the first milestone script-based and local-first. Separate the work into four units: API client, raw storage, normalization and quality checks, and a thin pipeline entry point so the connector can be tested in isolation and later extended without reshaping the whole codebase.

**Tech Stack:** Python 3.12, requests, pytest, pathlib, csv, json

---

## File structure

- `pyproject.toml` — Python project metadata and dependencies
- `ingestion/__init__.py` — package marker for importable ingestion code
- `ingestion/un/__init__.py` — package marker for UN source code
- `ingestion/un/reliefweb_client.py` — ReliefWeb API request building and fetch logic
- `ingestion/un/raw_store.py` — dated raw payload persistence helpers
- `ingestion/un/normalize.py` — canonical silver mapping logic
- `ingestion/un/quality.py` — silver-level validation and run summary helpers
- `ingestion/un/pipeline.py` — orchestration layer from fetch to silver output
- `scripts/run_reliefweb_pipeline.py` — local CLI entry point
- `tests/ingestion/un/test_imports.py` — package bootstrap test
- `tests/ingestion/un/test_reliefweb_client.py` — API and raw storage tests
- `tests/ingestion/un/test_normalize.py` — normalization and quality tests
- `tests/ingestion/un/test_pipeline.py` — end-to-end orchestration test

### Task 1: Bootstrap the Python package and test harness

**Files:**
- Create: `pyproject.toml`
- Create: `ingestion/__init__.py`
- Create: `ingestion/un/__init__.py`
- Create: `tests/ingestion/un/test_imports.py`

- [ ] **Step 1: Write the failing bootstrap test**

```python
# tests/ingestion/un/test_imports.py
from ingestion.un import __all__ as exported_names


def test_un_package_exports_reliefweb_modules():
    assert "reliefweb_client" in exported_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ingestion/un/test_imports.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'ingestion'`

- [ ] **Step 3: Write the minimal package scaffolding**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "jobs-wiki"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "requests>=2.32,<3",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0,<9",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# ingestion/__init__.py
"""Ingestion package for source-specific connectors."""
```

```python
# ingestion/un/__init__.py
"""UN source connectors."""

__all__ = ["reliefweb_client"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ingestion/un/test_imports.py -q`
Expected: PASS with `1 passed`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml ingestion/__init__.py ingestion/un/__init__.py tests/ingestion/un/test_imports.py
git commit -m "build: bootstrap python ingestion package"
```

### Task 2: Add the ReliefWeb client and raw payload storage

**Files:**
- Create: `ingestion/un/reliefweb_client.py`
- Create: `ingestion/un/raw_store.py`
- Create: `tests/ingestion/un/test_reliefweb_client.py`

- [ ] **Step 1: Write the failing client and raw-storage tests**

```python
# tests/ingestion/un/test_reliefweb_client.py
import json

from ingestion.un.raw_store import write_raw_payload
from ingestion.un.reliefweb_client import build_jobs_request, extract_jobs


def test_build_jobs_request_targets_reliefweb_jobs():
    payload = build_jobs_request(limit=5)

    assert payload["appname"] == "jobs_wiki"
    assert payload["limit"] == 5
    assert payload["preset"] == "latest"


def test_extract_jobs_returns_data_entries():
    response_json = {"data": [{"id": "job-1"}, {"id": "job-2"}]}

    assert extract_jobs(response_json) == response_json["data"]


def test_write_raw_payload_creates_dated_json_file(tmp_path):
    output_file = write_raw_payload(
        base_dir=tmp_path,
        run_date="2026-05-07",
        run_id="run-001",
        payload={"data": [{"id": "job-1"}]},
    )

    assert output_file.exists()
    assert output_file.name == "run-001.json"
    assert json.loads(output_file.read_text(encoding="utf-8"))["data"][0]["id"] == "job-1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ingestion/un/test_reliefweb_client.py -q`
Expected: FAIL with `ModuleNotFoundError` for `ingestion.un.raw_store` or `ingestion.un.reliefweb_client`

- [ ] **Step 3: Write the minimal client and raw-store implementation**

```python
# ingestion/un/reliefweb_client.py
from __future__ import annotations

from typing import Any


RELIEFWEB_JOBS_URL = "https://api.reliefweb.int/v1/jobs"


def build_jobs_request(limit: int = 100) -> dict[str, Any]:
    return {
        "appname": "jobs_wiki",
        "preset": "latest",
        "limit": limit,
    }


def extract_jobs(response_json: dict[str, Any]) -> list[dict[str, Any]]:
    return list(response_json.get("data", []))
```

```python
# ingestion/un/raw_store.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_raw_payload(
    base_dir: Path,
    run_date: str,
    run_id: str,
    payload: dict[str, Any],
) -> Path:
    target_dir = base_dir / "raw" / "reliefweb" / run_date
    target_dir.mkdir(parents=True, exist_ok=True)
    output_file = target_dir / f"{run_id}.json"
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_file
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ingestion/un/test_reliefweb_client.py -q`
Expected: PASS with `3 passed`

- [ ] **Step 5: Commit**

```bash
git add ingestion/un/reliefweb_client.py ingestion/un/raw_store.py tests/ingestion/un/test_reliefweb_client.py
git commit -m "feat: add reliefweb client and raw payload storage"
```

### Task 3: Add silver normalization and quality checks

**Files:**
- Create: `ingestion/un/normalize.py`
- Create: `ingestion/un/quality.py`
- Create: `tests/ingestion/un/test_normalize.py`

- [ ] **Step 1: Write the failing normalization and quality tests**

```python
# tests/ingestion/un/test_normalize.py
from ingestion.un.normalize import normalize_job
from ingestion.un.quality import summarize_quality


def test_normalize_job_maps_reliefweb_fields_to_canonical_schema():
    raw_job = {
        "id": "job-1",
        "fields": {
            "title": "Data Scientist",
            "url": "https://reliefweb.int/job/1",
            "body-html": "<p>Analyse data</p>",
            "source": [{"shortname": "ReliefWeb"}],
            "country": [{"name": "Kenya"}],
            "city": ["Nairobi"],
            "career_categories": [{"name": "Information Management"}],
            "closing-date": "2026-05-30T00:00:00+00:00",
            "date": {"created": "2026-05-01T00:00:00+00:00"},
        },
    }

    row = normalize_job(raw_job, run_id="run-001", ingested_at="2026-05-07T10:00:00Z")

    assert row["source"] == "reliefweb"
    assert row["source_job_id"] == "job-1"
    assert row["title"] == "Data Scientist"
    assert row["country"] == "Kenya"
    assert row["location"] == "Nairobi"
    assert row["url"] == "https://reliefweb.int/job/1"


def test_summarize_quality_counts_duplicates_and_missing_required_fields():
    rows = [
        {"source_job_id": "job-1", "url": "https://reliefweb.int/job/1", "title": "A"},
        {"source_job_id": "job-1", "url": "https://reliefweb.int/job/1", "title": "A"},
        {"source_job_id": "", "url": "", "title": "B"},
    ]

    summary = summarize_quality(rows)

    assert summary["record_count"] == 3
    assert summary["duplicate_source_job_ids"] == 1
    assert summary["missing_source_job_id"] == 1
    assert summary["missing_url"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ingestion/un/test_normalize.py -q`
Expected: FAIL with `ModuleNotFoundError` for `ingestion.un.normalize` or `ingestion.un.quality`

- [ ] **Step 3: Write the minimal normalization and quality implementation**

```python
# ingestion/un/normalize.py
from __future__ import annotations

from typing import Any


def _first_name(items: list[dict[str, Any]] | None) -> str:
    if not items:
        return ""
    return str(items[0].get("name", ""))


def normalize_job(raw_job: dict[str, Any], run_id: str, ingested_at: str) -> dict[str, str]:
    fields = raw_job.get("fields", {})
    cities = fields.get("city", [])
    created = fields.get("date", {}).get("created", "")

    return {
        "source": "reliefweb",
        "source_job_id": str(raw_job.get("id", "")),
        "title": str(fields.get("title", "")),
        "organization": _first_name(fields.get("source")),
        "location": str(cities[0]) if cities else "",
        "country": _first_name(fields.get("country")),
        "remote_flag": "",
        "contract_type": _first_name(fields.get("career_categories")),
        "grade": "",
        "posted_at": str(created),
        "closes_at": str(fields.get("closing-date", "")),
        "url": str(fields.get("url", "")),
        "description_text": str(fields.get("body-html", "")),
        "language": "en",
        "ingested_at": ingested_at,
        "run_id": run_id,
    }
```

```python
# ingestion/un/quality.py
from __future__ import annotations

from collections import Counter


def summarize_quality(rows: list[dict[str, str]]) -> dict[str, int]:
    id_counts = Counter(row.get("source_job_id", "") for row in rows if row.get("source_job_id"))

    return {
        "record_count": len(rows),
        "duplicate_source_job_ids": sum(1 for count in id_counts.values() if count > 1),
        "missing_source_job_id": sum(1 for row in rows if not row.get("source_job_id")),
        "missing_url": sum(1 for row in rows if not row.get("url")),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ingestion/un/test_normalize.py -q`
Expected: PASS with `2 passed`

- [ ] **Step 5: Commit**

```bash
git add ingestion/un/normalize.py ingestion/un/quality.py tests/ingestion/un/test_normalize.py
git commit -m "feat: add silver normalization and quality checks"
```

### Task 4: Wire the pipeline and local CLI entry point

**Files:**
- Create: `ingestion/un/pipeline.py`
- Create: `scripts/run_reliefweb_pipeline.py`
- Create: `tests/ingestion/un/test_pipeline.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing orchestration test**

```python
# tests/ingestion/un/test_pipeline.py
import csv
import json

from ingestion.un.pipeline import run_pipeline


def test_run_pipeline_writes_raw_silver_and_summary(tmp_path):
    def fake_fetch():
        return {
            "data": [
                {
                    "id": "job-1",
                    "fields": {
                        "title": "Data Scientist",
                        "url": "https://reliefweb.int/job/1",
                        "body-html": "<p>Analyse data</p>",
                        "source": [{"shortname": "ReliefWeb"}],
                        "country": [{"name": "Kenya"}],
                        "city": ["Nairobi"],
                        "career_categories": [{"name": "Information Management"}],
                        "closing-date": "2026-05-30T00:00:00+00:00",
                        "date": {"created": "2026-05-01T00:00:00+00:00"},
                    },
                }
            ]
        }

    result = run_pipeline(
        base_dir=tmp_path,
        run_date="2026-05-07",
        run_id="run-001",
        ingested_at="2026-05-07T10:00:00Z",
        fetch_payload=fake_fetch,
    )

    assert result["raw_path"].exists()
    assert result["silver_path"].exists()
    assert result["summary_path"].exists()

    with result["silver_path"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["source_job_id"] == "job-1"

    summary = json.loads(result["summary_path"].read_text(encoding="utf-8"))
    assert summary["record_count"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ingestion/un/test_pipeline.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'ingestion.un.pipeline'`

- [ ] **Step 3: Write the minimal pipeline and CLI implementation**

```python
# ingestion/un/pipeline.py
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from ingestion.un.normalize import normalize_job
from ingestion.un.quality import summarize_quality
from ingestion.un.raw_store import write_raw_payload


def run_pipeline(
    base_dir: Path,
    run_date: str,
    run_id: str,
    ingested_at: str,
    fetch_payload: Callable[[], dict[str, Any]],
) -> dict[str, Path]:
    payload = fetch_payload()
    raw_path = write_raw_payload(base_dir=base_dir, run_date=run_date, run_id=run_id, payload=payload)

    rows = [normalize_job(job, run_id=run_id, ingested_at=ingested_at) for job in payload.get("data", [])]

    silver_dir = base_dir / "silver" / "reliefweb" / run_date
    silver_dir.mkdir(parents=True, exist_ok=True)
    silver_path = silver_dir / f"{run_id}.csv"

    fieldnames = list(rows[0].keys()) if rows else [
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
```

```python
# scripts/run_reliefweb_pipeline.py
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import requests

from ingestion.un.pipeline import run_pipeline
from ingestion.un.reliefweb_client import RELIEFWEB_JOBS_URL, build_jobs_request


def fetch_payload() -> dict:
    response = requests.post(RELIEFWEB_JOBS_URL, json=build_jobs_request(), timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    now = datetime.now(UTC)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    run_pipeline(
        base_dir=Path("data"),
        run_date=now.strftime("%Y-%m-%d"),
        run_id=run_id,
        ingested_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        fetch_payload=fetch_payload,
    )
    print(f"ReliefWeb pipeline completed for run {run_id}")
```

````markdown
## Local pilot execution

Install the local Python environment:

```bash
python -m pip install -e .[dev]
```

Run the ReliefWeb pilot pipeline:

```bash
python scripts/run_reliefweb_pipeline.py
```

Expected outputs:

- `data/raw/reliefweb/<run-date>/<run-id>.json`
- `data/silver/reliefweb/<run-date>/<run-id>.csv`
- `data/runs/reliefweb/<run-date>/<run-id>.json`
````

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ingestion/un/test_pipeline.py tests/ingestion/un/test_reliefweb_client.py tests/ingestion/un/test_normalize.py -q`
Expected: PASS with `6 passed`

- [ ] **Step 5: Verify the package install and CLI run**

Run: `python -m pip install -e .[dev]`
Expected: editable install succeeds

Run: `python scripts/run_reliefweb_pipeline.py`
Expected: prints `ReliefWeb pipeline completed for run ...` and writes files under `data\raw\reliefweb\`, `data\silver\reliefweb\`, and `data\runs\reliefweb\`

- [ ] **Step 6: Commit**

```bash
git add ingestion/un/pipeline.py scripts/run_reliefweb_pipeline.py tests/ingestion/un/test_pipeline.py README.md
git commit -m "feat: wire local reliefweb pipeline entry point"
```

## Self-review checklist

- Spec coverage: raw persistence, canonical silver mapping, quality summary, local command entry point, and README usage are each covered by Tasks 2 through 4.
- Placeholder scan: no `TODO`, `TBD`, or "similar to previous task" shortcuts remain.
- Type consistency: `run_id`, `run_date`, `ingested_at`, `source_job_id`, and `fetch_payload` use the same names across all tasks.

## Implementation findings

### Issue 1: Exported module was not actually importable

- **Found in:** Task 1 quality review
- **Problem:** `ingestion/un/__init__.py` exported `reliefweb_client`, but the module did not exist yet, so the bootstrap test could pass while real imports still failed.
- **Resolution:** Added a minimal placeholder `ingestion/un/reliefweb_client.py` and strengthened the bootstrap test to import the module instead of only checking the `__all__` string list.

### Issue 2: Raw payload writer allowed path traversal through `run_id`

- **Found in:** Task 2 quality review
- **Problem:** `write_raw_payload` used `run_id` directly in the output filename path, which could allow writes outside the intended directory if unsafe values were passed.
- **Resolution:** Added defensive validation to reject unsafe `run_id` values containing path separators or traversal fragments, and added focused tests for the rejection behavior.

### Issue 3: Raw payload writer also allowed path traversal through `run_date`

- **Found in:** Task 2 follow-up quality review
- **Problem:** The first fix secured `run_id` but left `run_date` unchecked, which still allowed directory escape patterns.
- **Resolution:** Applied the same validation rule to `run_date` and added a focused regression test covering unsafe values.

### Issue 4: `extract_jobs` mishandled malformed API payloads

- **Found in:** Task 2 quality review and follow-up review
- **Problem:** `extract_jobs` originally failed on `{\"data\": null}` and could silently corrupt data by iterating non-list values such as strings.
- **Resolution:** Tightened the extractor so it returns an empty list unless `data` is a list, and added regression tests for `null` and non-list payloads.

### Issue 5: Python cache artifacts were accidentally committed

- **Found in:** Controller inspection after Task 2 fix commit
- **Problem:** A follow-up commit unintentionally included tracked `__pycache__` and `.pyc` files, which should not be versioned.
- **Resolution:** Removed the tracked cache artifacts, updated `.gitignore` to exclude Python cache files, and verified the worktree returned to a clean git state.

### Issue 6: Organization mapping missed ReliefWeb `shortname`

- **Found in:** Task 3 quality review
- **Problem:** The first normalization pass only read `name`, while ReliefWeb source metadata used `shortname`, so `organization` was coming through empty.
- **Resolution:** Updated `_first_name` to prefer `shortname` and fall back to `name`, then added assertions to verify `organization` is populated correctly.

### Issue 7: Duplicate reporting hid duplicate severity

- **Found in:** Task 3 quality review
- **Problem:** `duplicate_source_job_ids` counted how many distinct IDs were duplicated, but not how many extra duplicate rows existed.
- **Resolution:** Kept the original metric and added `total_duplicate_records` so the summary captures both duplicate spread and duplicate volume.

### Issue 8: Location extraction accepted bad first city values

- **Found in:** Task 3 quality review
- **Problem:** The first implementation used the first city entry directly, which could yield empty strings or `None`-derived values instead of the first meaningful city.
- **Resolution:** Added `_first_meaningful_city` so normalization skips empty and null entries and returns the first usable city value.

### Issue 9: Dict city entries and `None` IDs were normalized incorrectly

- **Found in:** Task 3 quality review
- **Problem:** City dictionaries were being stringified instead of extracting a label, and `None` source IDs became the literal string `"None"`.
- **Resolution:** Updated city normalization to extract `name` or `shortname` from dict entries and made `source_job_id` treat `None` as missing.

### Issue 10: Malformed ReliefWeb shapes could crash normalization

- **Found in:** Task 3 quality review
- **Problem:** Non-dict `date` values and non-list `source`, `country`, `career_categories`, or `city` values could raise exceptions during normalization.
- **Resolution:** Hardened normalization helpers with type guards so malformed shapes now resolve to empty strings instead of crashing.

### Issue 11: Quality metrics treated `None` values as real data

- **Found in:** Task 3 quality review
- **Problem:** `summarize_quality` stringified `None` into `"None"`, which caused missing IDs and URLs to be counted as present and could also create false duplicates.
- **Resolution:** Normalized `None` to empty values before trimming or duplicate counting, and added regression tests for `None` IDs and URLs.

### Issue 12: Some normalized string fields still emitted literal `"None"`

- **Found in:** Task 3 spec compliance review
- **Problem:** `closes_at`, `url`, `description_text`, then later `title` and `posted_at`, still converted explicit `None` values into the literal string `"None"`.
- **Resolution:** Introduced `_safe_str` and applied it to the affected normalized fields, then added focused tests for each `None` case.

### Issue 13: `fields: None` crashed the normalizer

- **Found in:** Task 3 quality review
- **Problem:** `normalize_job` assumed `raw_job["fields"]` was dict-like, so payloads containing `{"fields": null}` raised `AttributeError`.
- **Resolution:** Changed the normalizer to coerce a present-but-`None` `fields` value to an empty dict and added a regression test for that payload shape.

### Issue 14: Whitespace-only `shortname` values bypassed fallback logic

- **Found in:** Task 3 quality review
- **Problem:** `_first_name` treated whitespace-only `shortname` values as valid and returned them instead of falling back to `name`.
- **Resolution:** Trimmed candidate values before accepting them and added a test to verify whitespace-only `shortname` falls back to `name`.

### Issue 15: Bogus falsy placeholders leaked into normalized names

- **Found in:** Task 3 quality review
- **Problem:** `_first_name` could stringify placeholder values like `0` or `False` into normalized output.
- **Resolution:** Rejected boolean placeholders and numeric zero before stringification, while preserving fallback behavior to the next usable value.

### Current implementation status

- **Completed and committed:** Task 1 bootstrap, Task 2 ReliefWeb client/raw storage, and the current Task 3 normalization and quality work.
- **Pushed branch state:** ready to push as the latest partial implementation snapshot on `copilot/reliefweb-pilot`.
- **Still pending:** Task 4 pipeline and CLI wiring.
- **Known remaining follow-up:** review feedback still suggests tightening `_first_meaningful_city` and `_safe_str` against bogus boolean / zero placeholder values, even though the current test suite passes.

