from typing import Any

from benchling_sdk.models.webhooks.v0 import (
    WebhookEnvelopeV0,
    CanvasInitializeWebhookV0,
    CanvasInteractionWebhookV0,
)

from local_app.bootstrap import init_app_from_webhook
from local_app.views.canvas_initialize import show_search
from local_app.views.canvas_interaction import route_interaction_webhook


class UnsupportedWebhookError(Exception):
    pass


def handle_webhook(webhook_dict: dict[str, Any]) -> None:
    webhook = WebhookEnvelopeV0.from_dict(webhook_dict)
    app = init_app_from_webhook(webhook)
    # Could also choose to route on webhook.message.type
    if isinstance(webhook.message, CanvasInitializeWebhookV0):
        show_search(app, webhook.message)
    elif isinstance(webhook.message, CanvasInteractionWebhookV0):
        route_interaction_webhook(app, webhook.message)
    else:
        # Should only happen if the app's manifest requests webhooks that aren't handled in its code paths
        raise UnsupportedWebhookError(f"Received an unsupported webhook type: {webhook}")
