

import json
from unittest.mock import MagicMock, patch

import pytest
from benchling_sdk.apps.canvas.framework import CanvasBuilder
from benchling_sdk.apps.canvas.types import UiBlock
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.status.errors import AppUserFacingError
from benchling_sdk.apps.status.framework import SessionContextManager
from benchling_sdk.apps.types import JsonType
from benchling_sdk.models import AppCanvas, AppCanvasUpdate, Molecule, TextInputUiBlock
from benchling_sdk.models.webhooks.v0 import CanvasInteractionWebhookV2

from local_app.benchling_app.canvas_interaction import UnsupportedButtonError, route_interaction_webhook
from local_app.benchling_app.views.canvas_initialize import input_blocks
from local_app.benchling_app.views.constants import (
    CANCEL_BUTTON_ID,
    CID_KEY,
    CREATE_BUTTON_ID,
    SEARCH_BUTTON_ID,
    SEARCH_TEXT_ID,
)


class TestCanvasInteraction:

    @patch("local_app.benchling_app.canvas_interaction.render_preview_canvas")
    @patch("local_app.benchling_app.canvas_interaction.search")
    def test_route_interaction_webhook_search(self, mock_search, mock_render_preview_canvas) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", SEARCH_BUTTON_ID)
        mock_search_input = MagicMock(TextInputUiBlock)
        mock_search_input.id = SEARCH_TEXT_ID
        mock_search_input.value = "User Input"
        mock_canvas = _mock_canvas([mock_search_input])
        mock_session_context_manager = MagicMock()
        mock_session_context = MagicMock(SessionContextManager)
        mock_session_context_manager.__enter__.return_value = mock_session_context
        app.create_session_context.return_value = mock_session_context_manager
        app.benchling.apps.get_canvas_by_id.return_value = mock_canvas
        mock_search.return_value = {"cid": "example"}
        expected_canvas_builder = CanvasBuilder.from_canvas(mock_canvas)

        # Test
        route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.get_canvas_by_id.assert_called_once_with("canvas_id")
        mock_render_preview_canvas.assert_called_once_with(
            {"cid": "example"},
            "canvas_id",
            expected_canvas_builder,
            mock_session_context,
        )
        # Our sanitization will HTML encode the space
        mock_search.assert_called_once_with("User%20Input")
        mock_session_context.attach_canvas.assert_called_once_with("canvas_id")

    @patch("local_app.benchling_app.canvas_interaction.render_preview_canvas")
    @patch("local_app.benchling_app.canvas_interaction.search")
    def test_route_interaction_webhook_search_no_value(self, mock_search, mock_render_preview_canvas) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", SEARCH_BUTTON_ID)
        mock_search_input = MagicMock(TextInputUiBlock)
        mock_search_input.id = SEARCH_TEXT_ID
        mock_search_input.value = ""
        mock_canvas = _mock_canvas([mock_search_input])
        mock_session_context_manager = MagicMock()
        mock_session_context = MagicMock(SessionContextManager)
        mock_session_context_manager.__enter__.return_value = mock_session_context
        app.create_session_context.return_value = mock_session_context_manager
        app.benchling.apps.get_canvas_by_id.return_value = mock_canvas

        # Test
        with pytest.raises(AppUserFacingError, match="Please enter a chemical name to search for"):
            route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.get_canvas_by_id.assert_called_once_with("canvas_id")
        mock_render_preview_canvas.assert_not_called()
        mock_search.assert_not_called()
        mock_session_context.attach_canvas.assert_called_once_with("canvas_id")

    @patch("local_app.benchling_app.canvas_interaction.render_preview_canvas")
    @patch("local_app.benchling_app.canvas_interaction.search")
    def test_route_interaction_webhook_search_invalid_characters(
        self,
        mock_search,
        mock_render_preview_canvas,
    ) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", SEARCH_BUTTON_ID)
        mock_search_input = MagicMock(TextInputUiBlock)
        mock_search_input.id = SEARCH_TEXT_ID
        mock_search_input.value = "<(Invalid #!)>"
        mock_canvas = _mock_canvas([mock_search_input])
        mock_session_context_manager = MagicMock()
        mock_session_context = MagicMock(SessionContextManager)
        mock_session_context_manager.__enter__.return_value = mock_session_context
        app.create_session_context.return_value = mock_session_context_manager
        app.benchling.apps.get_canvas_by_id.return_value = mock_canvas

        # Test
        with pytest.raises(AppUserFacingError,
                           match="The chemical name can only contain letters, numbers, spaces, and hyphens"):
            route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.get_canvas_by_id.assert_called_once_with("canvas_id")
        mock_render_preview_canvas.assert_not_called()
        mock_search.assert_not_called()
        mock_session_context.attach_canvas.assert_called_once_with("canvas_id")

    def test_route_interaction_webhook_cancel(self) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", CANCEL_BUTTON_ID)
        mock_canvas = _mock_canvas()
        app.benchling.apps.get_canvas_by_id.return_value = mock_canvas
        expected_canvas_builder = CanvasBuilder.from_canvas(mock_canvas)\
            .with_enabled()\
            .with_session_id(None)\
            .with_blocks(input_blocks())
        expected_update = expected_canvas_builder.to_update()

        # Test
        route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.get_canvas_by_id.assert_called_once_with("canvas_id")
        app.benchling.apps.update_canvas.assert_called_once_with("canvas_id", expected_update)

    @patch("local_app.benchling_app.canvas_interaction.render_completed_canvas")
    @patch("local_app.benchling_app.canvas_interaction.create_molecule")
    @patch("local_app.benchling_app.canvas_interaction.get_by_cid")
    def test_route_interaction_webhook_create_molecule(
        self,
        mock_get_by_cid,
        mock_create_molecule,
        mock_render_completed_canvas,
    ) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", CREATE_BUTTON_ID)
        mock_canvas = _mock_canvas(data={CID_KEY: "Test-CID"})
        mock_session_context_manager = MagicMock()
        mock_session_context = MagicMock(SessionContextManager)
        mock_session_context_manager.__enter__.return_value = mock_session_context
        app.create_session_context.return_value = mock_session_context_manager
        app.benchling.apps.get_canvas_by_id.return_value = mock_canvas
        molecule_cid_data = {"CID": "Sample"}
        mock_get_by_cid.return_value = molecule_cid_data
        mock_molecule = MagicMock(Molecule)
        mock_create_molecule.return_value = mock_molecule
        expected_canvas_builder = CanvasBuilder.from_canvas(mock_canvas)

        # Test
        route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.get_canvas_by_id.assert_called_once_with("canvas_id")
        mock_render_completed_canvas.assert_called_once_with(
            mock_molecule,
            "canvas_id",
            expected_canvas_builder,
            mock_session_context,
        )
        mock_get_by_cid.assert_called_once_with("Test-CID")
        mock_create_molecule.assert_called_once_with(app, molecule_cid_data)
        mock_session_context.attach_canvas.assert_called_once_with("canvas_id")


    def test_route_interaction_webhook_unspported_button(self) -> None:
        app = MagicMock(App)
        interaction_webhook = _mock_interaction_webhook("canvas_id", "not-a-button-in-our-canvas")
        app.benchling.apps.get_canvas_by_id.return_value = MagicMock(AppCanvas)
        expected_update = AppCanvasUpdate(enabled=True)

        # Test
        with pytest.raises(UnsupportedButtonError):
            route_interaction_webhook(app, interaction_webhook)

        # Verify
        app.benchling.apps.update_canvas.assert_called_once_with("canvas_id", expected_update)


def _mock_canvas(blocks: list[UiBlock] | None = None, data: JsonType | None = None) -> AppCanvas:
    mock_canvas = MagicMock(AppCanvas)
    mock_canvas.blocks = blocks if blocks else []
    mock_canvas.data = json.dumps(data) if data is not None else None
    return mock_canvas


def _mock_interaction_webhook(canvas_id: str, button_id: str) -> CanvasInteractionWebhookV2:
    interaction_webhook = MagicMock(CanvasInteractionWebhookV2)
    interaction_webhook.button_id = button_id
    interaction_webhook.canvas_id = canvas_id
    return interaction_webhook
