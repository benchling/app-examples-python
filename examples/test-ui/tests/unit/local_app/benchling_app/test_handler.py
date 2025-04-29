from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.status.errors import AppUserFacingError

from local_app.benchling_app.handler import UnsupportedWebhookError, handle_webhook
from tests.helpers import load_webhook_json

_TEST_FILES_PATH = Path(__file__).parent.parent.parent.parent / "files/webhooks"


class TestWebhookHandler:

    @patch("local_app.benchling_app.handler.render_search_canvas")
    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_canvas_initialize(self, mock_init_app_from_webhook,
                                              mock_render_search_canvas) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        handle_webhook(webhook.to_dict())
        mock_render_search_canvas.assert_called_once_with(mock_app, webhook.message)

    @patch("local_app.benchling_app.handler.route_interaction_webhook")
    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_canvas_interaction(self,
                                               mock_init_app_from_webhook,
                                               mock_route_interaction_webhook) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_interaction_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        handle_webhook(webhook.to_dict())
        mock_route_interaction_webhook.assert_called_once_with(mock_app, webhook.message)

    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_unsupported(self, mock_init_app_from_webhook) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "app_activation_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        with pytest.raises(UnsupportedWebhookError):
            handle_webhook(webhook.to_dict())

    @patch("local_app.benchling_app.handler.logger")
    @patch("local_app.benchling_app.handler.render_search_canvas")
    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_user_error(self,
                                       mock_init_app_from_webhook,
                                       mock_render_search_canvas,
                                       mock_logger) -> None:
        webhook = load_webhook_json(_TEST_FILES_PATH / "canvas_initialize_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        mock_error = AppUserFacingError("Client error")
        mock_render_search_canvas.side_effect = [mock_error]
        handle_webhook(webhook.to_dict())
        mock_logger.debug.assert_has_calls(
            [call("Exiting with client error: %s", mock_error)],
            any_order=True,
        )
