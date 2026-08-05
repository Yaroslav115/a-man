"""Database URL normalization for SQLAlchemy's Psycopg dialect."""


def sqlalchemy_url(database_url: str) -> str:
    """Select SQLAlchemy's Psycopg 3 driver for a PostgreSQL URL."""

    if database_url.startswith("postgresql+psycopg://"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    return database_url
