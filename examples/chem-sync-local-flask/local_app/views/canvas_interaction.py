import re

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.models import Molecule, AppCanvasUpdate
from benchling_sdk.models.webhooks.v0 import CanvasInteractionWebhookV0

from local_app.pub_chem import search, get_by_cid
from local_app.molecules import create_molecule
from local_app.views.canvas_initialize import input_blocks
from local_app.views.chemical_preview import show_preview
from local_app.views.completed import show_completed
from local_app.views.constants import (
    SEARCH_BUTTON_ID,
    CANCEL_BUTTON_ID,
    CREATE_BUTTON_ID,
    SEARCH_TEXT_ID,
    CHEMICAL_PREVIEW_ID,
)


class UnsupportedButtonError(Exception):
    pass


def route_interaction_webhook(app: App, canvas_interaction: CanvasInteractionWebhookV0) -> None:
    canvas_id = canvas_interaction.canvas_id
    try:
        if canvas_interaction.button_id == SEARCH_BUTTON_ID:
            with app.create_session_context("Search Chemicals", timeout_seconds=20) as session:
                session.attach_canvas(canvas_id)
                canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
                canvas_inputs = canvas_builder.inputs_to_dict_single_value()
                _validate_inputs(canvas_inputs)
                results = search(canvas_inputs[SEARCH_TEXT_ID])
                show_preview(results, canvas_id, canvas_builder, session)
        elif canvas_interaction.button_id == CANCEL_BUTTON_ID:
            # Set session_id = None to detach and prior state or messages (essentially, reset)
            app.benchling.apps.update_canvas(
                canvas_id,
                AppCanvasUpdate(enabled=True, session_id=None, blocks=input_blocks()),
            )
        elif canvas_interaction.button_id == CREATE_BUTTON_ID:
            with app.create_session_context("Create Molecules", timeout_seconds=20) as session:
                session.attach_canvas(canvas_id)
                canvas_builder = _canvas_builder_from_canvas_id(app, canvas_id)
                molecule = _create_molecule_from_canvas(app, canvas_builder)
                show_completed(molecule, canvas_id, canvas_builder, session)
        else:
            # Not shown to user by default, for our own logs cause we forgot to handle some button
            raise UnsupportedButtonError(
                f"Whoops, the developer forgot to handle the button {canvas_interaction.button_id}"
            )
    # App Status contexts will handle writing messages back to the user, but we still need to re-enable
    # the canvas in the event of an error
    except BaseException:
        app.benchling.apps.update_canvas(canvas_id, AppCanvasUpdate(enabled=True))
        raise


def _create_molecule_from_canvas(app: App, canvas_builder: CanvasBuilder) -> Molecule:
    # Not a great way at the moment to persist data across Canvases without forcing the app to be stateful
    # So just pull it out of the Markdown where we displayed it. Lets Benchling "store" the "state"
    chemical_preview = canvas_builder.blocks.get_by_id(CHEMICAL_PREVIEW_ID).to_api_model().value
    matches = re.search("CID[^0-9a-zA-Z]*([a-zA-Z0-9]+)", chemical_preview)
    # # Only needed for type safety
    # assert matches is not None
    chemical_cid = matches.group(1)
    chemical = get_by_cid(chemical_cid)
    return create_molecule(app, chemical)


def _canvas_builder_from_canvas_id(app: App, canvas_id: str) -> CanvasBuilder:
    current_canvas = app.benchling.apps.get_canvas_by_id(canvas_id)
    return CanvasBuilder.from_canvas(current_canvas)


def _validate_inputs(inputs: dict[str, str]):
    if not inputs[SEARCH_TEXT_ID]:
        # AppFacingUserError is a special error that will propagate the error message as-is back to the user
        # via the App's session and end control flow
        raise AppUserFacingError("Please enter a chemical name to search for")