from __future__ import annotations

from collections import Counter


def summarize_quality(rows: list[dict[str, str]]) -> dict[str, int]:
    id_counts = Counter(row.get("source_job_id", "") for row in rows if row.get("source_job_id"))

    # Number of distinct IDs that appear more than once
    duplicate_ids = sum(1 for count in id_counts.values() if count > 1)
    # Total number of duplicate rows (excluding the first occurrence for each duplicated id)
    total_duplicate_records = sum(count - 1 for count in id_counts.values() if count > 1)

    return {
        "record_count": len(rows),
        "duplicate_source_job_ids": duplicate_ids,
        "total_duplicate_records": total_duplicate_records,
        "missing_source_job_id": sum(1 for row in rows if not row.get("source_job_id")),
        "missing_url": sum(1 for row in rows if not row.get("url")),
    }
