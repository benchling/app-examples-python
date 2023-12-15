from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.framework import App
from benchling_sdk.models import (
    MarkdownUiBlock,
    MarkdownUiBlockType,
    TextInputUiBlock,
    TextInputUiBlockType,
    ButtonUiBlock,
    ButtonUiBlockType,
)
from benchling_sdk.models.webhooks.v0 import CanvasInitializeWebhookV0

from local_app.views.constants import SEARCH_TEXT_ID, SEARCH_BUTTON_ID


def show_search(app: App, canvas_initialized: CanvasInitializeWebhookV0) -> None:
    with app.create_session_context("Show Sync Search", timeout_seconds=20):
        canvas_builder = CanvasBuilder(
            app_id=app.id,
            feature_id=canvas_initialized.feature_id,
            resource_id=canvas_initialized.resource_id,
        )
        canvas_builder.blocks.append(input_blocks())
        app.benchling.apps.create_canvas(canvas_builder.to_create())


def input_blocks():
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
