from __future__ import annotations

from typing import Any


def _first_name(items: list[dict[str, Any]] | None) -> str:
    """Return the most appropriate short name from a list of ReliefWeb-style dicts.

    Prefer 'shortname' (used by ReliefWeb), falling back to 'name' to preserve
    existing behavior for other sources (countries, categories, etc.).
    """
    if not items:
        return ""
    first = items[0]
    return str(first.get("shortname") or first.get("name") or "")


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
