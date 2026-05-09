import json
import pytest

from ingestion.un.raw_store import write_raw_payload
from ingestion.un.reliefweb_client import build_jobs_request, extract_jobs


def test_build_jobs_request_targets_reliefweb_jobs():
    payload = build_jobs_request(limit=5)

    assert payload["appname"] == "jobs_wiki"
    assert payload["limit"] == 5
    assert payload["preset"] == "latest"


def test_extract_jobs_returns_data_entries():
    response_json = {"data": [{"id": "job-1"}, {"id": "job-2"}]}

    assert extract_jobs(response_json) == response_json["data"]


def test_extract_jobs_handles_null_data():
    response_json = {"data": None}

    assert extract_jobs(response_json) == []


def test_write_raw_payload_creates_dated_json_file(tmp_path):
    output_file = write_raw_payload(
        base_dir=tmp_path,
        run_date="2026-05-07",
        run_id="run-001",
        payload={"data": [{"id": "job-1"}]},
    )

    assert output_file.exists()
    assert output_file.name == "run-001.json"
    assert json.loads(output_file.read_text(encoding="utf-8"))["data"][0]["id"] == "job-1"


def test_write_raw_payload_rejects_unsafe_run_id(tmp_path):
    with pytest.raises(ValueError):
        write_raw_payload(base_dir=tmp_path, run_date="2026-05-07", run_id="../evil", payload={})

    with pytest.raises(ValueError):
        write_raw_payload(base_dir=tmp_path, run_date="2026-05-07", run_id="unsafe/run", payload={})
