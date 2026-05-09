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
    # Reject run_id containing path separators or traversal fragments to prevent path traversal
    if not run_id or any(sep in run_id for sep in ("/", "\\", "..")):
        raise ValueError("unsafe run_id")

    target_dir = base_dir / "raw" / "reliefweb" / run_date
    target_dir.mkdir(parents=True, exist_ok=True)
    output_file = target_dir / f"{run_id}.json"
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_file
