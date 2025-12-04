from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.canvas.types import UiBlock
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.apps.status.helpers import ref
from benchling_sdk.models import (
    AppSessionMessageCreate,
    AppSessionMessageStyle,
    AppSessionUpdateStatus,
    MarkdownUiBlock,
    MarkdownUiBlockType,
    Molecule,
)


def render_archived_canvas(
    molecule: Molecule,
    canvas_id: str,
    canvas_builder: CanvasBuilder,
    session: SessionContextManager,
) -> None:
    canvas_builder = canvas_builder.with_blocks(_archived_blocks())
    session.app.benchling.apps.update_canvas(
        canvas_id,
        canvas_builder.with_enabled().to_update(),
    )
    session.close_session(
        AppSessionUpdateStatus.SUCCEEDED,
        messages=[
            AppSessionMessageCreate(
                # ref() will turn supported objects into clickable "chips" in the Benchling UI
                f"Chemical has been archived successfully!",
                style=AppSessionMessageStyle.SUCCESS,
            ),
            AppSessionMessageCreate(
                f"You can still view archived entities: {ref(molecule)}",
                style=AppSessionMessageStyle.INFO,
            ),
        ],
    )


def _archived_blocks() -> list[UiBlock]:
    return [
        MarkdownUiBlock(
            id="archived",
            type=MarkdownUiBlockType.MARKDOWN,
            value="The chemical has been archived.",
        ),
    ]
