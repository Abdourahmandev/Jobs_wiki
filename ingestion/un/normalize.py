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


def _first_meaningful_city(cities: list | None) -> str:
    """Return the first meaningful city string from a list.

    Skip None, empty strings, and whitespace-only entries. Return a trimmed
    string for the first non-empty value or an empty string if none found.
    """
    if not cities:
        return ""
    for c in cities:
        if c is None:
            continue
        s = str(c).strip()
        if s:
            return s
    return ""


def normalize_job(raw_job: dict[str, Any], run_id: str, ingested_at: str) -> dict[str, str]:
    fields = raw_job.get("fields", {})
    cities = fields.get("city", [])
    created = fields.get("date", {}).get("created", "")

    return {
        "source": "reliefweb",
        "source_job_id": str(raw_job.get("id", "")),
        "title": str(fields.get("title", "")),
        "organization": _first_name(fields.get("source")),
        # Use the first meaningful city entry (skip empty/null/whitespace values)
        "location": _first_meaningful_city(cities),
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
