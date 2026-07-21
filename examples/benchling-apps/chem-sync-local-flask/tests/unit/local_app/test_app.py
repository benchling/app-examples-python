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
    @patch("local_app.app.app_definition_id")
    @patch("local_app.app.verify")
    def test_app_receive_webhook(
        self,
        mock_verify,
        mock_app_definition_id,
        mock_enqueue_work,
        client,
    ) -> None:
        mock_app_definition_id.return_value = "appdef_123"
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        response = client.post(
            "1/webhooks/canvas",
            json=webhook.to_dict(),
            headers={
                "Webhook-Id": "msg_123",
                "Webhook-Timestamp": "1234567890",
                "Webhook-Signature": "v1,signature",
            },
        )
        assert response.status_code == 200
        assert mock_verify.call_args.args[0] == "appdef_123"
        assert "webhook-id" in mock_verify.call_args.args[2]
        mock_app_definition_id.assert_called_once()
        mock_enqueue_work.assert_called_once()
