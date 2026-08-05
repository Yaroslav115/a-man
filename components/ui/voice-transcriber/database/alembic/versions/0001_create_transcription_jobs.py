"""Create the transcription job journal.

This revision doubles as a bridge from the original SQL migration runner. If
the journal tables already exist, Alembic adopts them as its baseline.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if not context.is_offline_mode():
        inspector = sa.inspect(op.get_bind())
        existing_tables = set(inspector.get_table_names())
        if "transcription_jobs" in existing_tables:
            if "transcription_job_events" not in existing_tables:
                raise RuntimeError(
                    "Existing transcription_jobs schema is incomplete: "
                    "transcription_job_events is missing"
                )
            return

    op.create_table(
        "transcription_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("audio_path", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column(
            "include_segments",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("requested_model", sa.String(length=100), nullable=True),
        sa.Column("engine_name", sa.String(length=100), nullable=True),
        sa.Column("engine_version", sa.String(length=100), nullable=True),
        sa.Column(
            "attempt_number",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("worker_id", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("detected_language", sa.String(length=32), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "attempt_number >= 0", name="transcription_jobs_attempt_number_check"
        ),
        sa.CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0",
            name="transcription_jobs_size_bytes_check",
        ),
        sa.CheckConstraint(
            "source_type IN ('server_path', 'upload')",
            name="transcription_jobs_source_type_check",
        ),
        sa.CheckConstraint(
            "status IN ('created', 'queued', 'processing', 'completed', "
            "'failed', 'cancelled')",
            name="transcription_jobs_status_check",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "transcription_jobs_status_created_at_idx",
        "transcription_jobs",
        ["status", "created_at"],
    )
    op.create_table(
        "transcription_job_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["transcription_jobs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "transcription_job_events_job_id_occurred_at_idx",
        "transcription_job_events",
        ["job_id", "occurred_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "transcription_job_events_job_id_occurred_at_idx",
        table_name="transcription_job_events",
    )
    op.drop_table("transcription_job_events")
    op.drop_index(
        "transcription_jobs_status_created_at_idx",
        table_name="transcription_jobs",
    )
    op.drop_table("transcription_jobs")
