from __future__ import annotations

from collections import Counter


def _normalize_field(value: object) -> str | None:
    """Treat None as missing before any stringification or trimming.

    Returns the trimmed string when meaningful, otherwise None.
    """
    if value is None:
        return None
    s = str(value).strip()
    return s if s != "" else None


def summarize_quality(rows: list[dict[str, object]]) -> dict[str, int]:
    # Normalize source_job_id values treating None as missing before stringification
    normalized_ids = [_normalize_field(row.get("source_job_id")) for row in rows]
    non_empty_ids = [v for v in normalized_ids if v is not None]
    id_counts = Counter(non_empty_ids)

    # Number of distinct IDs that appear more than once
    duplicate_ids = sum(1 for count in id_counts.values() if count > 1)
    # Total number of duplicate rows (excluding the first occurrence for each duplicated id)
    total_duplicate_records = sum(count - 1 for count in id_counts.values() if count > 1)

    # Missing counts: None or empty/whitespace-only are treated as missing
    missing_source_job_id = sum(1 for v in normalized_ids if v is None)
    normalized_urls = [_normalize_field(row.get("url")) for row in rows]
    missing_url = sum(1 for v in normalized_urls if v is None)

    return {
        "record_count": len(rows),
        "duplicate_source_job_ids": duplicate_ids,
        "total_duplicate_records": total_duplicate_records,
        "missing_source_job_id": missing_source_job_id,
        "missing_url": missing_url,
    }
