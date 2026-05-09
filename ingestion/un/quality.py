from __future__ import annotations

from collections import Counter


def summarize_quality(rows: list[dict[str, str]]) -> dict[str, int]:
    # Explicitly only consider non-empty, non-whitespace source_job_id values
    # when detecting duplicates. Rows with missing or whitespace-only IDs are
    # counted as missing (see 'missing_source_job_id') and are not treated as
    # duplicates.
    non_empty_ids = [str(row.get("source_job_id", "")).strip() for row in rows if str(row.get("source_job_id", "")).strip()]
    id_counts = Counter(non_empty_ids)

    # Number of distinct IDs that appear more than once
    duplicate_ids = sum(1 for count in id_counts.values() if count > 1)
    # Total number of duplicate rows (excluding the first occurrence for each duplicated id)
    total_duplicate_records = sum(count - 1 for count in id_counts.values() if count > 1)

    return {
        "record_count": len(rows),
        "duplicate_source_job_ids": duplicate_ids,
        "total_duplicate_records": total_duplicate_records,
        # Treat empty or whitespace-only IDs as missing
        "missing_source_job_id": sum(1 for row in rows if not str(row.get("source_job_id", "")).strip()),
        # Treat empty or whitespace-only URLs as missing
        "missing_url": sum(1 for row in rows if not str(row.get("url", "")).strip()),
    }
