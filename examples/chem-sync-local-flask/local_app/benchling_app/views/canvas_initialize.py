from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.canvas.types import UiBlock
from benchling_sdk.apps.framework import App
from benchling_sdk.models import (
    ButtonUiBlock,
    ButtonUiBlockType,
    MarkdownUiBlock,
    MarkdownUiBlockType,
    TextInputUiBlock,
    TextInputUiBlockType,
)
from benchling_sdk.models.webhooks.v0 import (
    CanvasCreatedWebhookV2Beta,
    CanvasInitializeWebhookV2,
)

from local_app.benchling_app.views.constants import SEARCH_BUTTON_ID, SEARCH_TEXT_ID

"""
This file contains examples of how to handle different Canvas Webhooks

Use a CanvasBuilder to create or update a canvas associated with your app 
This sdk tool can be used for easy creation and updates

Check out https://benchling.com/sdk-docs/1.22.0/benchling_sdk.apps.canvas.framework.html
for more details on the CanvasBuilder class
"""


def render_search_canvas(app: App, canvas_initialized: CanvasInitializeWebhookV2) -> None:
    with app.create_session_context("Show Sync Search", timeout_seconds=20):
        canvas_builder = CanvasBuilder(
            app_id=app.id,
            feature_id=canvas_initialized.feature_id,
            resource_id=canvas_initialized.resource_id,
        )

        # Add the input blocks to the canvas 
        canvas_builder.blocks.append(input_blocks())

        # Create the canvas
        app.benchling.apps.create_canvas(canvas_builder.to_create())


def render_search_canvas_for_created_canvas(app: App, canvas_created: CanvasCreatedWebhookV2Beta) -> None:
    with app.create_session_context("Show Sync Search", timeout_seconds=20):
        canvas_builder = CanvasBuilder(app_id=app.id, feature_id=canvas_created.feature_id)
        canvas_builder.blocks.append(input_blocks())
        app.benchling.apps.update_canvas(canvas_created.canvas_id, canvas_builder.to_update())


def input_blocks() -> list[UiBlock]:
    """
    Create 3 blocks to populate the canvas: 

    Markdown block to display text 
    TextInput block to capture user input 
    Button block to trigger the search 
    """
    return [
        MarkdownUiBlock(
            id="top_instructions",
            type=MarkdownUiBlockType.MARKDOWN,
            value="Enter a chemical name to search. For example, _'aspirin'_",
        ),
        TextInputUiBlock(
            id=SEARCH_TEXT_ID,
            type=TextInputUiBlockType.TEXT_INPUT,
            placeholder="Chemical name to search...",
            value="",
        ),
        ButtonUiBlock(
            id=SEARCH_BUTTON_ID,
            text="Search Chemicals",
            type=ButtonUiBlockType.BUTTON,
        ),
    ]
