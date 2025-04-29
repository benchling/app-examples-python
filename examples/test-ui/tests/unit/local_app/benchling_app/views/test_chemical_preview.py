from unittest.mock import MagicMock, patch

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.canvas.types import UiBlock
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.models import (
    AppCanvas,
    AppSessionMessageCreate,
    AppSessionMessageStyle,
    AppSessionUpdateStatus,
    ButtonUiBlock,
    ButtonUiBlockType,
    MarkdownUiBlock,
    MarkdownUiBlockType,
    SectionUiBlock,
    SectionUiBlockType,
)

from local_app.benchling_app.views.canvas_initialize import input_blocks
from local_app.benchling_app.views.chemical_preview import render_preview_canvas
from local_app.benchling_app.views.constants import (
    CANCEL_BUTTON_ID,
    CID_KEY,
    CREATE_BUTTON_ID,
    SEARCH_TEXT_ID,
)


class TestChemicalPreview:

    @patch("local_app.benchling_app.views.chemical_preview.image_url")
    def test_render_preview_canvas_with_results(self, mock_image_url) -> None:
        mock_session = MagicMock(SessionContextManager)
        results = [
            {
                "name": "Test Chemical",
                "smiles": "010101",
                "cid": "test_cid",
            },
        ]
        mock_image_url.return_value = "https://images.benchling.com"
        mock_expected_canvas = MagicMock(AppCanvas)
        expected_canvas_builder = CanvasBuilder.from_canvas(mock_expected_canvas)\
            .with_enabled()\
            .with_data({CID_KEY: "test_cid"})\
            .with_blocks(_expected_preview_blocks())

        # Test
        render_preview_canvas(results, "canvas_id", expected_canvas_builder, mock_session)

        # Verify
        mock_session.app.benchling.apps.update_canvas.assert_called_once_with(
            "canvas_id",
            expected_canvas_builder.to_update(),
        )

    def test_render_preview_canvas_no_results(self) -> None:
        mock_session = MagicMock(SessionContextManager)
        original_canvas = MagicMock(AppCanvas)
        original_canvas_builder = CanvasBuilder.from_canvas(original_canvas).with_blocks(input_blocks())
        # Set an input value
        original_canvas_builder.blocks.get_by_id(SEARCH_TEXT_ID).to_api_model().value = "User Input"
        expected_canvas_builder = CanvasBuilder.from_canvas(original_canvas)\
            .with_enabled()\
            .with_blocks(input_blocks())


        # Test
        render_preview_canvas(None, "canvas_id", original_canvas_builder, mock_session)

        # Verify
        mock_session.app.benchling.apps.update_canvas.assert_called_once_with(
            "canvas_id",
            expected_canvas_builder.to_update(),
        )
        mock_session.close_session.assert_called_once_with(
            AppSessionUpdateStatus.SUCCEEDED,
            messages=[
                AppSessionMessageCreate(
                    "Couldn't find any chemicals for 'User Input'",
                    style=AppSessionMessageStyle.INFO,
                ),
            ],
        )


def _expected_preview_blocks() -> list[UiBlock]:
    return [
        MarkdownUiBlock(
            id="results",
            type=MarkdownUiBlockType.MARKDOWN,
            value="We found the following chemical based on your search:",
        ),
        MarkdownUiBlock(
            id="chemical_preview",
            type=MarkdownUiBlockType.MARKDOWN,
            value=(
                "**Name**: Test Chemical\n\n**Structure**: 010101"
            ),
        ),
        MarkdownUiBlock(
            id="chemical_image",
            type=MarkdownUiBlockType.MARKDOWN,
            value="![Test Chemical](https://images.benchling.com)",
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
