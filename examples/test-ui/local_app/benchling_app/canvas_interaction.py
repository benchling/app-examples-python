import re
from typing import cast
from urllib.parse import quote

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.models import AppCanvasUpdate
from benchling_sdk.models.webhooks.v0 import CanvasInteractionWebhookV2
from local_app.benchling_app.views.constants import (
    CANCEL_BUTTON_ID,
    CREATE_BUTTON_ID,
    SEARCH_BUTTON_ID,
    SEARCH_TEXT_ID,
)

from local_app.benchling_app.views.canvas_initialize import input_blocks
from local_app.benchling_app.views.completed import render_completed_canvas
from local_app.lib.logger import get_logger

logger = get_logger()

class UnsupportedButtonError(Exception):
    pass


def route_interaction_webhook(app: App, canvas_interaction: CanvasInteractionWebhookV2) -> None:
    canvas_id = canvas_interaction.canvas_id
    if canvas_interaction.button_id == SEARCH_BUTTON_ID:
        with app.create_session_context("Submit", timeout_seconds=20) as session:
            session.attach_canvas(canvas_id)
            canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
            canvas_inputs = canvas_builder.inputs_to_dict_single_value()
            sanitized_inputs = _validate_and_sanitize_inputs(canvas_inputs)
            results = {}
            render_completed_canvas(results, canvas_id, canvas_builder, session)
    elif canvas_interaction.button_id == CANCEL_BUTTON_ID:
        # Set session_id = None to detach and prior state or messages (essentially, reset)
        canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
        canvas_update = canvas_builder.with_enabled()\
            .with_session_id(None)\
            .with_blocks(input_blocks())\
            .to_update()
        app.benchling.apps.update_canvas(canvas_id, canvas_update)
    else:
        # Re-enable the Canvas, or it will stay disabled and the user will be stuck
        app.benchling.apps.update_canvas(canvas_id, AppCanvasUpdate(enabled=True))
        # Not shown to user by default, for our own logs cause we forgot to handle some button
        # This is developer error
        raise UnsupportedButtonError(
            f"Whoops, the developer forgot to handle the button {canvas_interaction.button_id}",
        )

def _canvas_builder_from_canvas_id(app: App, canvas_id: str) -> CanvasBuilder:
    current_canvas = app.benchling.apps.get_canvas_by_id(canvas_id)
    return CanvasBuilder.from_canvas(current_canvas)

def _validate_and_sanitize_inputs(inputs: dict[str, str]) -> dict[str, str]:
    sanitized_inputs = {}
    if not inputs[SEARCH_TEXT_ID]:
        # AppFacingUserError is a special error that will propagate the error message as-is back to the user
        # via the App's session and end control flow
        raise AppUserFacingError("Please enter something")
    if not re.match("^[a-zA-Z\\d\\s\\-]+$", inputs[SEARCH_TEXT_ID]):
        raise AppUserFacingError("The input can only contain letters, numbers, spaces, and hyphens")
    sanitized_inputs[SEARCH_TEXT_ID] = quote(inputs[SEARCH_TEXT_ID])
    return sanitized_inputs
