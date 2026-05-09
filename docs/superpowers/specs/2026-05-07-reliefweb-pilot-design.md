# ReliefWeb pilot pipeline design

## Problem

The repository has a clear target architecture, but no implemented data pipeline yet. The next step is to prove the project can ingest one real source end to end in a local-first setup before expanding to ML, API, frontend, cloud, or multi-source orchestration.

## Design goal

Deliver one reliable local pipeline for the UN-adjacent ReliefWeb jobs source that:

1. fetches real job data from ReliefWeb
2. stores immutable dated raw outputs locally
3. transforms raw data into a canonical silver dataset
4. runs explicit data-quality checks
5. emits a run summary that makes the execution auditable

## Scope

### In scope

- ReliefWeb jobs as the only pilot source
- Local execution with Python scripts
- Raw and silver data layers stored locally
- One canonical jobs schema for silver
- Run-level logging and summary output
- Documentation updates in the repository README

### Out of scope

- Model training
- FastAPI service
- Streamlit frontend
- Power BI reporting
- Cloud infrastructure and orchestration
- Multi-source ingestion

## Recommended approach

Use a connector-first approach.

The pilot should start by locking the ReliefWeb extraction contract and proving that one real connector can be run repeatedly without manual cleanup. This is preferable to starting with a broad cross-source abstraction or jumping early into model work, because it reduces unknowns and lets the team validate the data contract on a real source before scaling the architecture.

## Architecture

The milestone stays local-first and script-based.

1. A Python ingestion entry point calls the ReliefWeb API.
2. The raw response is persisted unchanged in a dated location.
3. A normalization step maps source fields into the canonical silver schema.
4. A validation step checks required fields, duplicates, and parseability of key values.
5. A run summary records counts, warnings, and failures for the execution.

This keeps the first milestone narrow, inspectable, and easy to debug while matching the repo's longer-term Bronze/Silver/Gold direction.

## Data outputs

### Raw layer

The raw layer stores the source payload exactly as returned, partitioned by run date. It acts as the immutable evidence trail for every execution and allows reprocessing without re-fetching when debugging or evolving transformations.

### Silver layer

The silver layer stores normalized job records in a canonical schema. The exact file format can stay simple at first, but the schema should be stable enough to support later training and source replication.

Recommended canonical fields:

- `source`
- `source_job_id`
- `title`
- `organization`
- `location`
- `country`
- `remote_flag`
- `contract_type`
- `grade`
- `posted_at`
- `closes_at`
- `url`
- `description_text`
- `language`
- `ingested_at`
- `run_id`

## Execution model

The milestone should be runnable from a single local command. Each run should write its outputs to dated folders and preserve enough intermediate evidence to debug failures without guessing what happened.

The pipeline should fail explicitly when:

- the API is unreachable
- the response format no longer matches expectations
- required data needed for the canonical schema is missing beyond agreed thresholds

Partial artifacts and logs should still be kept so the failure can be investigated.

## Quality rules

The silver output should enforce a small set of hard gates:

- every record must have a stable source identifier
- every record must have a navigable source URL
- duplicate jobs should be detected and counted
- date fields should be parsed when present
- missing critical fields should be counted and surfaced in the run summary

These checks are intentionally minimal. The goal is not perfect data on day one, but a trustworthy baseline that can be improved safely.

## Success criteria

The milestone is complete when one repeatable run against real ReliefWeb data:

1. fetches records successfully
2. stores raw data locally with a dated partition
3. produces a canonical silver dataset
4. generates a run summary with counts and quality signals
5. completes without manual data cleanup

## Follow-on work after this milestone

Once the pilot is stable, the next sequence should be:

1. strengthen silver transformations and quality rules
2. produce gold features for a local baseline model
3. replicate the same pattern to World Bank and AfDB
4. migrate the proven flow toward the cloud target architecture

