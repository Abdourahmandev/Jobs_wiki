from __future__ import annotations

from typing import Any


def _first_name(items: list[dict[str, Any]] | None) -> str:
    """Return the most appropriate short name from a list of ReliefWeb-style dicts.

    Prefer 'shortname' (used by ReliefWeb), falling back to 'name' to preserve
    existing behavior for other sources (countries, categories, etc.).

    Be tolerant of malformed shapes: if `items` is not a list, treat it as
    missing and return an empty string rather than raising an exception.
    """
    if not isinstance(items, list) or not items:
        return ""
    first = items[0]
    if not isinstance(first, dict):
        return ""
    # Prefer 'shortname' but treat whitespace-only values and bogus falsy
    # placeholders (booleans and numeric zeros) as unusable and fall back to 'name'.
    short = first.get("shortname")
    if short is not None:
        # Reject boolean values (True/False) which would stringify to 'True'/'False'
        # and numeric zero which would stringify to '0' — neither are meaningful.
        if isinstance(short, bool) or (isinstance(short, (int, float)) and short == 0):
            short_usable = False
        else:
            short_usable = True
        if short_usable:
            s = str(short).strip()
            if s:
                return s
    name = first.get("name")
    if name is not None:
        if isinstance(name, bool) or (isinstance(name, (int, float)) and name == 0):
            name_usable = False
        else:
            name_usable = True
        if name_usable:
            s = str(name).strip()
            if s:
                return s
    return ""


def _first_meaningful_city(cities: list | None) -> str:
    """Return the first meaningful city string from a list.

    Skip None, empty strings, whitespace-only entries, and dicts without a
    usable 'name' or 'shortname'. If a dict is encountered prefer extracting
    the 'name' (fall back to 'shortname') and return it if non-empty.

    Be tolerant of malformed shapes: only accept lists. If `cities` is not a
    list, return an empty string rather than iterating strings or dicts.
    """
    if not isinstance(cities, list) or not cities:
        return ""
    for c in cities:
        if c is None:
            continue
        # If the city is a dict, prefer the 'name' or 'shortname' keys
        if isinstance(c, dict):
            name = c.get("name") or c.get("shortname")
            if name is None:
                continue
            s = str(name).strip()
        else:
            s = str(c).strip()
        if s:
            return s
    return ""


def _safe_str(value: Any) -> str:
    """Convert a value to string, treating None as an empty string.

    This prevents values like None from being stringified to the literal
    'None' which is not desired for missing fields in the normalized output.
    """
    return "" if value is None else str(value)


def normalize_job(raw_job: dict[str, Any], run_id: str, ingested_at: str) -> dict[str, str]:
    fields = raw_job.get("fields") or {}
    cities = fields.get("city", [])
    date_field = fields.get("date")
    if isinstance(date_field, dict):
        created = date_field.get("created", "")
    else:
        created = ""

    # Treat None source IDs as missing (empty string), not the literal 'None'
    raw_id = raw_job.get("id", "")
    source_id = "" if raw_id is None else str(raw_id)

    return {
        "source": "reliefweb",
        "source_job_id": source_id,
        "title": _safe_str(fields.get("title", "")),
        "organization": _first_name(fields.get("source")),
        # Use the first meaningful city entry (skip empty/null/whitespace values)
        "location": _first_meaningful_city(cities),
        "country": _first_name(fields.get("country")),
        "remote_flag": "",
        "contract_type": _first_name(fields.get("career_categories")),
        "grade": "",
        "posted_at": _safe_str(created),
        "closes_at": _safe_str(fields.get("closing-date")),
        "url": _safe_str(fields.get("url")),
        "description_text": _safe_str(fields.get("body-html")),
        "language": "en",
        "ingested_at": ingested_at,
        "run_id": run_id,
    }
