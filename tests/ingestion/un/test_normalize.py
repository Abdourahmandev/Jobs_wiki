from ingestion.un.normalize import normalize_job
from ingestion.un.quality import summarize_quality


def test_normalize_job_maps_reliefweb_fields_to_canonical_schema():
    raw_job = {
        "id": "job-1",
        "fields": {
            "title": "Data Scientist",
            "url": "https://reliefweb.int/job/1",
            "body-html": "<p>Analyse data</p>",
            "source": [{"shortname": "ReliefWeb"}],
            "country": [{"name": "Kenya"}],
            "city": ["Nairobi"],
            "career_categories": [{"name": "Information Management"}],
            "closing-date": "2026-05-30T00:00:00+00:00",
            "date": {"created": "2026-05-01T00:00:00+00:00"},
        },
    }

    row = normalize_job(raw_job, run_id="run-001", ingested_at="2026-05-07T10:00:00Z")

    assert row["source"] == "reliefweb"
    assert row["source_job_id"] == "job-1"
    assert row["title"] == "Data Scientist"
    assert row["organization"] == "ReliefWeb"
    assert row["country"] == "Kenya"
    assert row["location"] == "Nairobi"
    assert row["url"] == "https://reliefweb.int/job/1"


def test_normalize_job_uses_first_meaningful_city():
    raw_job = {
        "id": "job-2",
        "fields": {
            "title": "Analyst",
            "city": ["", None, "  ", "Kampala", "Nairobi"],
        },
    }

    row = normalize_job(raw_job, run_id="run-002", ingested_at="2026-05-07T11:00:00Z")

    assert row["location"] == "Kampala"


def test_first_meaningful_city_handles_dict_entries():
    # Ensure dict city entries prefer 'name' and do not get stringified as a dict
    raw_job = {
        "id": "job-3",
        "fields": {
            "title": "Coordinator",
            "city": [{"name": "Lagos"}, None, ""],
        },
    }

    row = normalize_job(raw_job, run_id="run-003", ingested_at="2026-05-07T12:00:00Z")

    assert row["location"] == "Lagos"


def test_source_job_id_none_treated_as_missing():
    # When the source 'id' is None, normalize_job should return an empty string
    raw_job = {"id": None, "fields": {"title": "Tester"}}

    row = normalize_job(raw_job, run_id="run-004", ingested_at="2026-05-07T13:00:00Z")

    assert row["source_job_id"] == ""


def test_summarize_quality_treats_missing_ids_as_missing_not_duplicates():
    rows = [
        {"source_job_id": "", "url": "u1", "title": "X"},
        {"source_job_id": "   ", "url": "u2", "title": "Y"},
        {"source_job_id": "job-1", "url": "u3", "title": "A"},
        {"source_job_id": "job-1", "url": "u4", "title": "A"},
    ]

    summary = summarize_quality(rows)

    assert summary["duplicate_source_job_ids"] == 1
    assert summary["missing_source_job_id"] == 2
