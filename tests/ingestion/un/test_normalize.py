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


def test_summarize_quality_treats_none_ids_as_missing_not_duplicates():
    rows = [
        {"source_job_id": None, "url": "u1", "title": "X"},
        {"source_job_id": "job-1", "url": "u2", "title": "A"},
        {"source_job_id": "job-1", "url": "u3", "title": "A"},
    ]

    summary = summarize_quality(rows)

    assert summary["duplicate_source_job_ids"] == 1
    assert summary["missing_source_job_id"] == 1


def test_summarize_quality_treats_none_urls_as_missing():
    rows = [
        {"source_job_id": "job-1", "url": None, "title": "X"},
        {"source_job_id": "job-2", "url": "", "title": "Y"},
        {"source_job_id": "job-3", "url": "   ", "title": "Z"},
    ]

    summary = summarize_quality(rows)

    assert summary["missing_url"] == 3


def test_malformed_date_non_dict_returns_empty_posted_at():
    raw_job = {
        "id": "job-10",
        "fields": {
            "title": "Tester",
            # date should be a dict but here is a string
            "date": "2026-05-01T00:00:00+00:00",
        },
    }

    row = normalize_job(raw_job, run_id="run-010", ingested_at="2026-05-07T14:00:00Z")

    # Should not crash and should return empty posted_at for malformed date
    assert row["posted_at"] == ""


def test_first_name_handles_non_list_input_returns_empty():
    raw_job = {
        "id": "job-11",
        "fields": {
            # source/country/career_categories expected lists; supply dicts/strings
            "source": {"shortname": "ReliefWeb"},
            "country": "Kenya",
            "career_categories": {"name": "Information Management"},
        },
    }

    row = normalize_job(raw_job, run_id="run-011", ingested_at="2026-05-07T15:00:00Z")

    # Malformed shapes should yield empty strings, not crash or produce dict/stringified values
    assert row["organization"] == ""
    assert row["country"] == ""
    assert row["contract_type"] == ""


def test_first_meaningful_city_handles_non_list_input_returns_empty():
    # city as a bare string
    raw_job1 = {"id": "job-12", "fields": {"city": "Nairobi"}}
    row1 = normalize_job(raw_job1, run_id="run-012", ingested_at="2026-05-07T16:00:00Z")
    assert row1["location"] == ""

    # city as a dict (not in a list)
    raw_job2 = {"id": "job-13", "fields": {"city": {"name": "Lagos"}}}
    row2 = normalize_job(raw_job2, run_id="run-013", ingested_at="2026-05-07T16:00:00Z")
    assert row2["location"] == ""


def test_normalize_job_treats_none_fields_as_empty_strings():
    # Fields that are explicitly None should be normalized to empty strings
    raw_job = {
        "id": "job-20",
        "fields": {
            "title": "Tester",
            "closing-date": None,
            "url": None,
            "body-html": None,
        },
    }

    row = normalize_job(raw_job, run_id="run-020", ingested_at="2026-05-07T16:00:00Z")

    assert row["closes_at"] == ""
    assert row["url"] == ""
    assert row["description_text"] == ""


def test_first_name_whitespace_shortname_falls_back_to_name():
    raw_job = {
        "id": "job-21",
        "fields": {"source": [{"shortname": "   ", "name": "Valid Organization"}]},
    }

    row = normalize_job(raw_job, run_id="run-021", ingested_at="2026-05-07T17:00:00Z")

    assert row["organization"] == "Valid Organization"
