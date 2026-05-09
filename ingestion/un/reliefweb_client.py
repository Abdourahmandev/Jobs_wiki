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
    data = response_json.get("data", None)
    if data is None:
        return []
    return list(data)
