from pathlib import Path

import pytest
from benchling_sdk.apps.framework import App

from local_app.benchling_app.setup import _auth_method, app_definition_id, init_app_from_webhook
from tests.helpers import load_webhook_json

_TEST_FILES_PATH = Path(__file__).parent.parent.parent.parent / "files/webhooks"


class TestBenchlingAppSetup:

    def setup_method(self) -> None:
        _auth_method.cache_clear()
        app_definition_id.cache_clear()

    def test_init_app_from_webhook(self, monkeypatch) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        with monkeypatch.context() as context:
            context.setenv("CLIENT_ID", "clientId")
            context.setenv("CLIENT_SECRET_FILE", str(_TEST_FILES_PATH.parent / "test_client_secret"))
            result = init_app_from_webhook(webhook)
            assert isinstance(result, App)

    def test_init_app_from_webhook_missing_client_id(self, monkeypatch) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        with monkeypatch.context() as context:
            context.setenv("CLIENT_SECRET_FILE", str(_TEST_FILES_PATH.parent / "test_client_secret"))
            with pytest.raises(AssertionError, match="Missing CLIENT_ID from environment"):
                init_app_from_webhook(webhook)

    def test_init_app_from_webhook_missing_client_secret_file(self, monkeypatch) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        with monkeypatch.context() as context:
            context.setenv("CLIENT_ID", "clientId")
            with pytest.raises(AssertionError, match="Missing CLIENT_SECRET_FILE from environment"):
                init_app_from_webhook(webhook)

    def test_app_definition_id(self, monkeypatch) -> None:
        with monkeypatch.context() as context:
            context.setenv("APP_DEFINITION_ID", "app_def1234")
            result = app_definition_id()
            assert result == "app_def1234"

    def test_app_definition_id_missing_app_definition_id(self, monkeypatch) -> None:
        with (monkeypatch.context(),
              pytest.raises(AssertionError, match="Missing APP_DEFINITION_ID from environment")):
            app_definition_id()
