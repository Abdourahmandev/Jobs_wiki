from __future__ import annotations

from typing import Any

RELIEFWEB_JOBS_URL = "https://api.reliefweb.int/v2/jobs"
RELIEFWEB_APP_NAME = "jobs_wiki"


def build_jobs_request(limit: int = 100) -> dict[str, Any]:
    return {
        "preset": "latest",
        "limit": limit,
    }


def extract_jobs(response_json: dict[str, Any]) -> list[dict[str, Any]]:
    data = response_json.get("data", None)
    if data is None:
        return []
    # Only accept lists; protect against strings or other iterables being turned into lists
    if not isinstance(data, list):
        return []
    return data
