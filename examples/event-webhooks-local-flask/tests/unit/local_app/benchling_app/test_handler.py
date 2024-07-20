from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from benchling_sdk.models.webhooks.v0 import EventCreatedWebhookV0Beta
from benchling_sdk.apps.config.mock_config import MockConfigItemStore
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.helpers.manifest_helpers import manifest_from_file
from benchling_sdk.models import EntitySchemaAppConfigItem, EntitySchemaAppConfigItemType

from local_app.benchling_app.handler import UnsupportedWebhookError, handle_webhook
from tests.helpers import load_beta_webhook_json

_TEST_FILES_PATH = Path(__file__).parent.parent.parent.parent / "files/webhooks"


class TestWebhookHandler:

    @patch("local_app.benchling_app.handler.sync_event_data")
    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_event_created_entity_registered(self, mock_init_app_from_webhook,
                                              mock_sync_event_data) -> None:
        # Setup
        webhook = load_beta_webhook_json(_TEST_FILES_PATH / "entity_registered_webhook.json")
        mock_app = MagicMock(App)
        # The schema in App Config must match the webhook payload or our handler filter
        # will exclude this event. By default, App Config generates random values, so in
        # this case we need to set an explicit value
        manifest = manifest_from_file(Path(__file__).parent.parent.parent.parent.parent / "manifest.yaml")
        # This will mock all config items with random valid values
        # We can override particular configs if desired. This shows an example of overriding a schema config
        mock_config_store = MockConfigItemStore.from_manifest(manifest).with_replacement(
        EntitySchemaAppConfigItem(
            path=["Synced Schema"],
            # Must match what's in tests/files/webhooks/entity_registered_webhook.json
            value="ts_X3i4k1M0",
            type=EntitySchemaAppConfigItemType.ENTITY_SCHEMA),
        )
        mock_app.config_store = mock_config_store
        mock_init_app_from_webhook.return_value = mock_app

        # Test
        handle_webhook(webhook.to_dict())

        # Verify
        assert isinstance(webhook.message, EventCreatedWebhookV0Beta)
        mock_sync_event_data.assert_called_once_with(mock_app, webhook.message.event)

    @patch("local_app.benchling_app.handler.sync_event_data")
    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_event_created_ignores_other_event(self, mock_init_app_from_webhook,
                                              mock_sync_event_data) -> None:
        webhook = load_beta_webhook_json(_TEST_FILES_PATH / "assay_run_created_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        handle_webhook(webhook.to_dict())
        mock_sync_event_data.assert_not_called()

    @patch("local_app.benchling_app.handler.init_app_from_webhook")
    def test_handle_webhook_unsupported(self, mock_init_app_from_webhook) -> None:
        webhook = load_beta_webhook_json(_TEST_FILES_PATH / "app_activation_webhook.json")
        mock_app = MagicMock(App)
        mock_init_app_from_webhook.return_value = mock_app
        with pytest.raises(UnsupportedWebhookError):
            handle_webhook(webhook.to_dict())
