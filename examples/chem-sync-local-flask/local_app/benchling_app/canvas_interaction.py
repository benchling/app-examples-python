import re
from typing import cast
from urllib.parse import quote

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.models import AppCanvasUpdate, Molecule
from benchling_sdk.models.webhooks.v0 import CanvasInteractionWebhookV2

from local_app.benchling_app.molecules import create_molecule
from local_app.benchling_app.views.canvas_initialize import input_blocks
from local_app.benchling_app.views.chemical_preview import render_preview_canvas
from local_app.benchling_app.views.completed import render_completed_canvas
from local_app.benchling_app.views.constants import (
    CANCEL_BUTTON_ID,
    CID_KEY,
    CREATE_BUTTON_ID,
    SEARCH_BUTTON_ID,
    SEARCH_TEXT_ID,
)
from local_app.lib.logger import get_logger
from local_app.lib.pub_chem import get_by_cid, search

logger = get_logger()


class UnsupportedButtonError(Exception):
    pass


def route_interaction_webhook(app: App, canvas_interaction: CanvasInteractionWebhookV2) -> None:
    canvas_id = canvas_interaction.canvas_id
    if canvas_interaction.button_id == SEARCH_BUTTON_ID:
        with app.create_session_context("Search Chemicals", timeout_seconds=20) as session:
            session.attach_canvas(canvas_id)
            canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
            canvas_inputs = canvas_builder.inputs_to_dict_single_value()
            sanitized_inputs = _validate_and_sanitize_inputs(canvas_inputs)
            results = search(sanitized_inputs[SEARCH_TEXT_ID])
            render_preview_canvas(results, canvas_id, canvas_builder, session)
    elif canvas_interaction.button_id == CANCEL_BUTTON_ID:
        # Set session_id = None to detach and prior state or messages (essentially, reset)
        canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
        canvas_update = canvas_builder.with_enabled()\
            .with_session_id(None)\
            .with_blocks(input_blocks())\
            .to_update()
        app.benchling.apps.update_canvas(canvas_id, canvas_update)
    elif canvas_interaction.button_id == CREATE_BUTTON_ID:
        with app.create_session_context("Create Molecules", timeout_seconds=20) as session:
            session.attach_canvas(canvas_id)
            canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
            molecule = _create_molecule_from_canvas(app, canvas_builder)
            render_completed_canvas(molecule, canvas_id, canvas_builder, session)
    else:
        # Re-enable the Canvas, or it will stay disabled and the user will be stuck
        app.benchling.apps.update_canvas(canvas_id, AppCanvasUpdate(enabled=True))
        # Not shown to user by default, for our own logs cause we forgot to handle some button
        # This is developer error
        raise UnsupportedButtonError(
            f"Whoops, the developer forgot to handle the button {canvas_interaction.button_id}",
        )


def _create_molecule_from_canvas(app: App, canvas_builder: CanvasBuilder) -> Molecule:
    # JSON can be almost any type, cast only needed if you care about type safety checks like MyPy
    canvas_data = cast(dict, canvas_builder.data_to_json())
    # Only needed for type safety
    assert canvas_data is not None
    logger.debug("Canvas data: %s", canvas_data)
    chemical_cid = canvas_data[CID_KEY]
    chemical = get_by_cid(chemical_cid)
    return create_molecule(app, chemical)


def _canvas_builder_from_canvas_id(app: App, canvas_id: str) -> CanvasBuilder:
    current_canvas = app.benchling.apps.get_canvas_by_id(canvas_id)
    return CanvasBuilder.from_canvas(current_canvas)


def _validate_and_sanitize_inputs(inputs: dict[str, str]) -> dict[str, str]:
    sanitized_inputs = {}
    if not inputs[SEARCH_TEXT_ID]:
        # AppFacingUserError is a special error that will propagate the error message as-is back to the user
        # via the App's session and end control flow
        raise AppUserFacingError("Please enter a chemical name to search for")
    if not re.match("^[a-zA-Z\\d\\s\\-]+$", inputs[SEARCH_TEXT_ID]):
        raise AppUserFacingError("The chemical name can only contain letters, numbers, spaces, and hyphens")
    sanitized_inputs[SEARCH_TEXT_ID] = quote(inputs[SEARCH_TEXT_ID])
    return sanitized_inputs
