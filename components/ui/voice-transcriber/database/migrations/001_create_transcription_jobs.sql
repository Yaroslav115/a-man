BEGIN;

CREATE TABLE transcription_jobs (
    id UUID PRIMARY KEY,
    status VARCHAR(32) NOT NULL CHECK (
        status IN (
            'created', 'queued', 'processing', 'completed', 'failed', 'cancelled'
        )
    ),
    audio_path TEXT NOT NULL,
    source_type VARCHAR(32) NOT NULL CHECK (
        source_type IN ('server_path', 'upload')
    ),
    original_filename TEXT,
    content_type VARCHAR(255),
    size_bytes BIGINT CHECK (size_bytes IS NULL OR size_bytes >= 0),
    language VARCHAR(32),
    include_segments BOOLEAN NOT NULL DEFAULT TRUE,
    requested_model VARCHAR(100),
    engine_name VARCHAR(100),
    engine_version VARCHAR(100),
    attempt_number INTEGER NOT NULL DEFAULT 0 CHECK (attempt_number >= 0),
    worker_id TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    transcript_text TEXT,
    detected_language VARCHAR(32),
    result JSONB,
    error JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX transcription_jobs_status_created_at_idx
    ON transcription_jobs (status, created_at);

CREATE TABLE transcription_job_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES transcription_jobs(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX transcription_job_events_job_id_occurred_at_idx
    ON transcription_job_events (job_id, occurred_at, id);

COMMIT;
