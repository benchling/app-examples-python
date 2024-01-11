from typing import Any

from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.models.webhooks.v0 import (
    CanvasInitializeWebhookV0,
    CanvasInteractionWebhookV0,
    WebhookEnvelopeV0,
)

from local_app.benchling_app.canvas_interaction import route_interaction_webhook
from local_app.benchling_app.setup import init_app_from_webhook
from local_app.benchling_app.views.canvas_initialize import render_search_canvas
from local_app.lib.logger import get_logger

logger = get_logger()


class UnsupportedWebhookError(Exception):
    pass


def handle_webhook(webhook_dict: dict[str, Any]) -> None:
    logger.debug("Handling webhook with payload: %s", webhook_dict)
    webhook = WebhookEnvelopeV0.from_dict(webhook_dict)
    # TODO: Finish implementing intialize the app from webhook
    app = init_app_from_webhook(webhook)
    if isinstance(webhook.message, CanvasInitializeWebhookV0):
        render_search_canvas(app, webhook.message)
    # elif isinstance(webhook.message, CanvasInteractionWebhookV0):
    #     route_interaction_webhook(app, webhook.message)
    # else:
    #     raise UnsupportedWebhookError(f"Received an unsupported webhook type: {webhook}")
    # logger.debug("Successfully completed request for webhook: %s", webhook_dict)
