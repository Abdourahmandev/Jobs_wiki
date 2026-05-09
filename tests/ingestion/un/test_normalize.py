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
    assert row["country"] == "Kenya"
    assert row["location"] == "Nairobi"
    assert row["url"] == "https://reliefweb.int/job/1"


def test_summarize_quality_counts_duplicates_and_missing_required_fields():
    rows = [
        {"source_job_id": "job-1", "url": "https://reliefweb.int/job/1", "title": "A"},
        {"source_job_id": "job-1", "url": "https://reliefweb.int/job/1", "title": "A"},
        {"source_job_id": "", "url": "", "title": "B"},
    ]

    summary = summarize_quality(rows)

    assert summary["record_count"] == 3
    assert summary["duplicate_source_job_ids"] == 1
    assert summary["missing_source_job_id"] == 1
    assert summary["missing_url"] == 1
