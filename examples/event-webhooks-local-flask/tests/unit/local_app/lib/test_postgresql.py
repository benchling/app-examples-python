

from pathlib import Path
from unittest import mock

import pytest

from local_app.lib.postgresql import _database_password_from_file, write_data

_TEST_FILES_PATH = Path(__file__).parent.parent.parent.parent / "files"


class TestPostgreSql:
    # postgresql fixture provided by pytest-postgresql
    def test_write_data(self, monkeypatch, postgresql) -> None:
        with postgresql.cursor() as cursor:
            cursor.execute(_create_table_sql_from_file())
            with monkeypatch.context() as context:
                context.setenv("POSTGRES_PASSWORD_FILE", str(_TEST_FILES_PATH / "test_database_password"))
                with mock.patch("local_app.lib.postgresql._connection") as mock_connection:
                    mock_connection.return_value = postgresql
                    result = write_data("Entity Name", "API ID", "Field Value")
                    # The connection is closed so we can't query to verify the data
                    # Just verify that we returned an ID. The database should be empty, so ID should be 1
                    assert result == 1

    def test_write_data_field_value_none(self, monkeypatch, postgresql) -> None:
        with postgresql.cursor() as cursor:
            cursor.execute(_create_table_sql_from_file())
            with monkeypatch.context() as context:
                context.setenv("POSTGRES_PASSWORD_FILE", str(_TEST_FILES_PATH / "test_database_password"))
                with mock.patch("local_app.lib.postgresql._connection") as mock_connection:
                    mock_connection.return_value = postgresql
                    result = write_data("Entity Name", "API ID", None)
                    # The connection is closed so we can't query to verify the data
                    # Just verify that we returned an ID. The database should be empty, so ID should be 1
                    assert result == 1

    def test_database_password_from_file(self, monkeypatch) -> None:
        with monkeypatch.context() as context:
            context.setenv("POSTGRES_PASSWORD_FILE", str(_TEST_FILES_PATH / "test_database_password"))
            result = _database_password_from_file()
            assert result == "fake_password"

    def test_database_password_from_file_missing_file(self, monkeypatch) -> None:
        with (
                monkeypatch.context(),
                pytest.raises(AssertionError, match="Missing POSTGRES_PASSWORD_FILE from environment"),
            ):
            _database_password_from_file()


def _create_table_sql_from_file() -> str:
    create_table_sql_path = _TEST_FILES_PATH.parent.parent / "scripts/create_tables.sql"
    with create_table_sql_path.open() as f:
        return f.read()
