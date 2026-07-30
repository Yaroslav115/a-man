#!/bin/sh
set -eu

: "${TRANSCRIBER_DATABASE_URL:?TRANSCRIBER_DATABASE_URL is required}"

psql "$TRANSCRIBER_DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SQL

for migration in /migrations/*.sql; do
    filename=$(basename "$migration")
    applied=$(
        psql "$TRANSCRIBER_DATABASE_URL" \
            -v ON_ERROR_STOP=1 \
            -tAc "SELECT 1 FROM schema_migrations WHERE filename = '$filename'"
    )

    if [ "$applied" = "1" ]; then
        echo "Already applied: $filename"
        continue
    fi

    echo "Applying: $filename"
    psql "$TRANSCRIBER_DATABASE_URL" -v ON_ERROR_STOP=1 -f "$migration"
    psql "$TRANSCRIBER_DATABASE_URL" \
        -v ON_ERROR_STOP=1 \
        -c "INSERT INTO schema_migrations (filename) VALUES ('$filename')"
done
