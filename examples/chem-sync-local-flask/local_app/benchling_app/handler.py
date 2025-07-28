from typing import Any

from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.models.webhooks.v0 import (
    CanvasCreatedWebhookV2,
    CanvasInitializeWebhookV2,
    CanvasInteractionWebhookV2,
    WebhookEnvelopeV0,
)

from local_app.benchling_app.canvas_interaction import route_interaction_webhook
from local_app.benchling_app.setup import init_app_from_webhook
from local_app.benchling_app.views.canvas_initialize import (
    render_search_canvas,
    render_search_canvas_for_created_canvas,
)
from local_app.lib.logger import get_logger

logger = get_logger()


class UnsupportedWebhookError(Exception):
    pass


def handle_webhook(webhook_dict: dict[str, Any]) -> None:
    logger.debug("Handling webhook with payload: %s", webhook_dict)
    webhook = WebhookEnvelopeV0.from_dict(webhook_dict)
    app = init_app_from_webhook(webhook)
    # Could also choose to route on webhook.message.type
    # Note: if your manifest specifies more than one item in `features`,
    # then `webhook.message.feature_id` may also need to be part of your routing logic
    try:
        if isinstance(webhook.message, CanvasInitializeWebhookV2):
            render_search_canvas(app, webhook.message)
        elif isinstance(webhook.message, CanvasInteractionWebhookV2):
            route_interaction_webhook(app, webhook.message)
        elif isinstance(webhook.message, CanvasCreatedWebhookV2):
            render_search_canvas_for_created_canvas(app, webhook.message)
        else:
            # Should only happen if the app's manifest requests webhooks that aren't handled in its code paths
            raise UnsupportedWebhookError(f"Received an unsupported webhook type: {webhook}")
        logger.debug("Successfully completed request for webhook: %s", webhook_dict)
    # We want errors shown to the user to end control flow, but we don't want them to propagate
    # and show as errors in our logs.
    # For this example, Flask error handler won't intercept this since we're within a thread
    except AppUserFacingError as e:
        logger.debug("Exiting with client error: %s", e)
