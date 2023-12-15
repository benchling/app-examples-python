from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.status.framework import ref, SessionContextManager
from benchling_sdk.models import (
    MarkdownUiBlock,
    MarkdownUiBlockType,
    AppSessionUpdateStatus,
    AppSessionMessageStyle,
    AppSessionMessageCreate,
    Molecule,
)


def show_completed(
    molecule: Molecule,
    canvas_id: str,
    canvas_builder: CanvasBuilder,
    session: SessionContextManager,
):
    # Just take the first result, as an example
    canvas_builder = canvas_builder.with_blocks(_completed_blocks())
    session.app.benchling.apps.update_canvas(
        canvas_id,
        canvas_builder.with_enabled().to_update(),
    )
    session.close_session(
        AppSessionUpdateStatus.SUCCEEDED,
        messages=[
            AppSessionMessageCreate(
                # ref() will turn supported objects into clickable "chips" in the Benchling UI
                f"Created the molecule {ref(molecule)} in Benchling!",
                style=AppSessionMessageStyle.SUCCESS,
            )
        ],
    )


def _completed_blocks():
    return [
        MarkdownUiBlock(
            id="completed",
            type=MarkdownUiBlockType.MARKDOWN,
            value="The chemical has been synced into Benchling! Please follow procedures for next steps.",
        ),
    ]
