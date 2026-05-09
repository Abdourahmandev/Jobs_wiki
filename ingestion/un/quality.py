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
