from unittest.mock import MagicMock, patch

from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.canvas.types import UiBlock
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.models import (
    AppCanvas,
    AppSessionMessageCreate,
    AppSessionMessageStyle,
    AppSessionUpdateStatus,
    MarkdownUiBlock,
    MarkdownUiBlockType,
    Molecule,
)

from local_app.benchling_app.views.completed import render_completed_canvas


class TestCompleted:

    @patch("local_app.benchling_app.views.completed.ref")
    def test_render_completed_canvas(self, mock_ref) -> None:
        mock_session = MagicMock(SessionContextManager)
        molecule = MagicMock(Molecule)
        mock_ref.return_value = "(reference)"
        mock_canvas = MagicMock(AppCanvas)
        canvas_builder = CanvasBuilder.from_canvas(mock_canvas)
        expected_canvas_builder = CanvasBuilder.from_canvas(mock_canvas)\
            .with_blocks(_expected_completed_blocks())\
            .with_enabled()

        # Test
        render_completed_canvas(molecule, "canvas_id", canvas_builder, mock_session)

        # Verify
        mock_session.app.benchling.apps.update_canvas.assert_called_once_with(
            "canvas_id",
            expected_canvas_builder.to_update(),
        )
        mock_session.close_session.assert_called_once_with(
            AppSessionUpdateStatus.SUCCEEDED,
            messages=[
                AppSessionMessageCreate(
                    "Created the molecule (reference) in Benchling!",
                    style=AppSessionMessageStyle.SUCCESS,
                ),
            ],
        )
        mock_ref.assert_called_once_with(molecule)


def _expected_completed_blocks() -> list[UiBlock]:
    return [
        MarkdownUiBlock(
            id="completed",
            type=MarkdownUiBlockType.MARKDOWN,
            value="The chemical has been synced into Benchling! Please follow procedures for next steps.",
        ),
    ]
