from typing import Any

from benchling_sdk.apps.framework import App
from benchling_sdk.models.webhooks.v0 import (
    EntityRegisteredWebhookV2,
    WebhookEnvelopeV0,
)

from local_app.benchling_app.setup import init_app_from_webhook
from local_app.benchling_app.sync_data import sync_event_data
from local_app.lib.logger import get_logger

logger = get_logger()


class UnsupportedWebhookError(Exception):
    pass


def handle_webhook(webhook_dict: dict[str, Any]) -> None:
    logger.debug("Handling webhook with payload: %s", webhook_dict)
    webhook = WebhookEnvelopeV0.from_dict(webhook_dict)
    app = init_app_from_webhook(webhook)
    # Could also choose to route on webhook.message.type
    if isinstance(webhook.message, EntityRegisteredWebhookV2):
        # Since we'll be receiving ALL entity registrations, add a filter to only
        # work with events that meet our criteria (e.g., specific schema)
        if _is_target_event(app, webhook.message):
            sync_event_data(app, webhook.message)
        else:
            logger.debug("Discarded event and exiting: %s", webhook.message)
            return
    else:
        # Should only happen if the app's manifest requests webhooks that aren't handled in its code paths
        raise UnsupportedWebhookError(f"Received an unsupported webhook type: {webhook}")
    logger.debug("Successfully completed request for webhook: %s", webhook_dict)


def _is_target_event(app: App, webhook: EntityRegisteredWebhookV2) -> bool:
    # .required().value_str() are only needed for type safety checks like MyPy
    # If type safety isn't a concern:
    # `app.config_store.config_by_path(["Synced Schema"]).value`
    target_schema_id = app.config_store.config_by_path(["Synced Schema"]).required().value_str()
    assert webhook.schema
    return webhook.schema.id == target_schema_id
