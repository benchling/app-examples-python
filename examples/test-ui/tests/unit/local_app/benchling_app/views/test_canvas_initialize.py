from unittest.mock import MagicMock

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.framework import App
from benchling_sdk.models.webhooks.v0 import CanvasInitializeWebhookV2

from local_app.benchling_app.views.canvas_initialize import input_blocks, render_search_canvas


class TestCanvasInitialize:

    def test_render_search_canvas(self) -> None:
        initialize_webhook = MagicMock(CanvasInitializeWebhookV2)
        initialize_webhook.feature_id = "feature_id"
        initialize_webhook.resource_id = "resource_id"
        app = MagicMock(App)
        app.id = "app_id"
        expected_canvas_builder = CanvasBuilder(
            app_id="app_id",
            feature_id="feature_id",
            resource_id="resource_id",
            blocks=input_blocks(),
        )

        # Test
        render_search_canvas(app, initialize_webhook)

        # Verify
        app.benchling.apps.create_canvas.assert_called_once_with(expected_canvas_builder.to_create())
