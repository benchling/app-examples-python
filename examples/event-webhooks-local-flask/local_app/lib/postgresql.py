import os
from pathlib import Path

import psycopg2

from local_app.lib.logger import get_logger

logger = get_logger()


def write_data(entity_name: str, benchling_api_id: str, field_value: str | None) -> str:
    with _connection() as conn, conn.cursor() as cursor:
        insert_query = """
            INSERT INTO synced_benchling_data
            (entity_name, benchling_api_id, field_value) VALUES (%s, %s, %s)
            RETURNING synced_entity_id
        """
        insert_data = (entity_name, benchling_api_id, field_value)
        logger.debug("Inserting entity data as: %s", insert_data)
        # Security note: psycopg2 should sanitize user input to protect from SQL injection, etc.
        cursor.execute(insert_query, insert_data)
        result = cursor.fetchone()
        # Appease MyPy type checking
        assert result is not None
        synced_id = result[0]
        conn.commit()
        return synced_id


def _connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        database="benchling",
        user="postgres",
        host="external-database",
        port=5432,
        password=_database_password_from_file(),
    )


def _database_password_from_file() -> str:
    file_path = os.environ.get("POSTGRES_PASSWORD_FILE")
    assert file_path is not None, "Missing POSTGRES_PASSWORD_FILE from environment"
    with Path(file_path).open() as f:
        return f.read()
