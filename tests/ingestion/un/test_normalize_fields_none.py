from ingestion.un.normalize import normalize_job


def test_normalize_job_handles_fields_key_none():
    raw_job = {"id": "job-30", "fields": None}

    row = normalize_job(raw_job, run_id="run-030", ingested_at="2026-05-07T00:00:00Z")

    # Should not crash and should treat missing fields as empty strings
    assert row["title"] == ""
    assert row["url"] == ""
    assert row["description_text"] == ""
