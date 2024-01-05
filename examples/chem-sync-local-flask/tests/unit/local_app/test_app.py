from pathlib import Path
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from local_app.app import create_app
from tests.helpers import load_webhook_json

_TEST_FILES_PATH = Path(__file__).parent.parent.parent / "files/webhooks"


@pytest.fixture()
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


class TestApp:

    @patch("local_app.app._enqueue_work")
    @patch("local_app.app.verify_app_installation")
    def test_app_receive_webhook(self, mock_verify_app_installation, mock_enqueue_work, client) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        response = client.post("1/webhooks/canvas", json=webhook.to_dict())
        assert response.status_code == 200
        mock_verify_app_installation.assert_called_once()
        mock_enqueue_work.assert_called_once()
