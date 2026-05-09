from ingestion.un.normalize import normalize_job


def test_title_none_returns_empty_string():
    raw_job = {"id": "job-30", "fields": {"title": None}}

    row = normalize_job(raw_job, run_id="run-030", ingested_at="2026-05-07T00:00:00Z")

    assert row["title"] == ""


def test_posted_at_none_when_date_created_is_none():
    raw_job = {
        "id": "job-31",
        "fields": {"title": "X", "date": {"created": None}},
    }

    row = normalize_job(raw_job, run_id="run-031", ingested_at="2026-05-07T00:00:00Z")

    assert row["posted_at"] == ""
