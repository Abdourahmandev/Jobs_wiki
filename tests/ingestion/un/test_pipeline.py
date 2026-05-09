import csv
import json

from ingestion.un.pipeline import run_pipeline


def test_run_pipeline_writes_raw_silver_and_summary(tmp_path):
    def fake_fetch():
        return {
            "data": [
                {
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
            ]
        }

    result = run_pipeline(
        base_dir=tmp_path,
        run_date="2026-05-07",
        run_id="run-001",
        ingested_at="2026-05-07T10:00:00Z",
        fetch_payload=fake_fetch,
    )

    assert result["raw_path"].exists()
    assert result["silver_path"].exists()
    assert result["summary_path"].exists()

    with result["silver_path"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["source_job_id"] == "job-1"

    summary = json.loads(result["summary_path"].read_text(encoding="utf-8"))
    assert summary["record_count"] == 1
