from typing import Any

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.models import (
    AppSessionUpdateStatus,
    AppSessionMessageStyle,
    AppSessionMessageCreate,
    MarkdownUiBlock,
    MarkdownUiBlockType,
    SectionUiBlock,
    SectionUiBlockType,
    ButtonUiBlock,
    ButtonUiBlockType,
)

from local_app.pub_chem import image_url
from local_app.views.constants import (
    SEARCH_TEXT_ID,
    CHEMICAL_PREVIEW_ID,
    CREATE_BUTTON_ID,
    CANCEL_BUTTON_ID,
    CID_KEY,
)


def show_preview(
    results: list[dict[str, Any]] | None,
    canvas_id: str,
    canvas_builder: CanvasBuilder,
    session: SessionContextManager,
) -> None:
    if results:
        # Just take the first result, as an example
        chemical = results[0]
        # Add the result to the canvas as data that won't be shown to the user but can be retrieved later
        canvas_builder = canvas_builder.with_blocks(_preview_blocks(chemical)).with_data({CID_KEY: chemical["cid"]}).with_enabled()
        session.app.benchling.apps.update_canvas(
            canvas_id,
            canvas_builder.to_update(),
        )
    if not results:
        session.close_session(
            AppSessionUpdateStatus.SUCCEEDED,
            messages=[
                AppSessionMessageCreate(
                    f"Couldn't find any chemicals for '{canvas_builder.inputs_to_dict()[SEARCH_TEXT_ID]}'",
                    style=AppSessionMessageStyle.INFO,
                )
            ],
        )


def _preview_blocks(chemical: dict[str, Any]):
    return [
        MarkdownUiBlock(
            id="results",
            type=MarkdownUiBlockType.MARKDOWN,
            value="We found the following chemical based on your search:",
        ),
        MarkdownUiBlock(
            id=CHEMICAL_PREVIEW_ID,
            type=MarkdownUiBlockType.MARKDOWN,
            value=(
                f"**CID**: {chemical['cid']}\n**Name**: "
                f"{chemical['name']}\n**Structure**: {chemical['smiles']}"
            ),
        ),
        MarkdownUiBlock(
            id="chemical_image",
            type=MarkdownUiBlockType.MARKDOWN,
            value=f'![{chemical["name"]}]({image_url(chemical["cid"])})',
        ),
        MarkdownUiBlock(
            id="user_prompt",
            type=MarkdownUiBlockType.MARKDOWN,
            value="Would you like to create it in Benchling?",
        ),
        SectionUiBlock(
            id="preview_buttons",
            type=SectionUiBlockType.SECTION,
            children=[
                ButtonUiBlock(
                    id=CREATE_BUTTON_ID,
                    text="Create Molecule",
                    type=ButtonUiBlockType.BUTTON,
                ),
                ButtonUiBlock(
                    id=CANCEL_BUTTON_ID,
                    text="Cancel",
                    type=ButtonUiBlockType.BUTTON,
                ),
            ],
        ),
    ]
