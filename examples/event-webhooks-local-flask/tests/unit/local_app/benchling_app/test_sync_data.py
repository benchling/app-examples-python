from pathlib import Path
from unittest.mock import MagicMock, patch

from benchling_api_client.webhooks.v0.beta.models.v2_entity_registered_event import (
    V2EntityRegisteredEvent as V2EntityRegisteredEventBeta,
)
from benchling_sdk.apps.config.mock_config import MockConfigItemStore
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.helpers.manifest_helpers import manifest_from_file
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.apps.status.helpers import ref
from benchling_sdk.helpers.serialization_helpers import fields
from benchling_sdk.models import (
    AppSessionMessageCreate,
    AppSessionMessageStyle,
    AppSessionUpdateStatus,
    CustomEntity,
    FieldAppConfigItem,
    FieldAppConfigItemType,
    LinkedAppConfigResourceSummary,
)

from local_app.benchling_app.sync_data import _sync_entity, sync_event_data


class TestSyncData:
    @patch("local_app.benchling_app.sync_data._sync_entity")
    def test_sync_event_data(self, mock_sync_entity) -> None:
        # Setup
        entity = MagicMock(CustomEntity)
        app = MagicMock(App)
        mock_session_context_manager = MagicMock()
        mock_session_context = MagicMock(SessionContextManager)
        mock_session_context_manager.__enter__.return_value = mock_session_context
        app.create_session_context.return_value = mock_session_context_manager
        app.benchling.custom_entities.get_by_id.return_value = entity
        mock_sync_entity.return_value = "database_id"
        entity_registered = MagicMock(V2EntityRegisteredEventBeta)
        entity_registered.resource_id = "resource_id"

        # Test
        sync_event_data(app, entity_registered)

        # Verify
        app.benchling.custom_entities.get_by_id.assert_called_once_with("resource_id")
        mock_sync_entity.assert_called_once_with(app, entity)
        mock_session_context.close_session.assert_called_once_with(
            status=AppSessionUpdateStatus.SUCCEEDED,
            messages=[
                AppSessionMessageCreate(
                    f"Synced {ref(entity)} into external database with ID database_id",
                    style=AppSessionMessageStyle.SUCCESS,
                ),
            ],
        )

    @patch("local_app.benchling_app.sync_data.write_data")
    def test_sync_entity(self, mock_write_data) -> None:
        # Setup
        mock_app = MagicMock(App)
        mock_entity = MagicMock(CustomEntity)
        mock_entity.name = "Entity Name"
        mock_entity.id = "API ID"
        mock_entity.fields = fields({"Configured Field": {"value": "Sync Value"}})
        manifest = manifest_from_file(Path(__file__).parent.parent.parent.parent.parent / "manifest.yaml")
        # This will mock all config items with random valid values
        # We can override particular configs if desired. This shows an example of overriding a folder config
        mock_config_store = MockConfigItemStore.from_manifest(manifest).with_replacement(
            FieldAppConfigItem(
                path=["Synced Schema", "Synced Field Data"],
                value="tsf_123",
                type=FieldAppConfigItemType.FIELD,
                linked_resource=LinkedAppConfigResourceSummary(id="tsf_123", name="Configured Field"),
            ),
        )
        mock_app.config_store = mock_config_store

        # Test
        _sync_entity(mock_app, mock_entity)

        # Verify
        mock_write_data.assert_called_once_with("Entity Name", "API ID", "Sync Value")
