import json
from pathlib import Path
from unittest.mock import call, patch

from httpx import Response

from local_app.lib.pub_chem import _pubchem_get, get_by_cid, image_url, search

_TEST_FILES_PATH = Path(__file__).parent.parent.parent.parent / "files/pubchem"


class TestPubChem:

    def setup_method(self) -> None:
        _pubchem_get.cache_clear()

    @patch("local_app.lib.pub_chem.get_by_cid")
    @patch("local_app.lib.pub_chem.httpx")
    def test_search(self, mock_httpx, mock_get_by_cid) -> None:
        response_json = _load_pubchem_json(_TEST_FILES_PATH / "search.json")
        mock_httpx.get.return_value = _mock_httpx_json_response(response_json)
        mock_get_by_cid.return_value = {
            "cid": 2244,
        }
        result = search("search_cid")
        assert [{"cid": 2244}] == result
        mock_httpx.get.assert_called_once_with("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/search_cid/cids/JSON?MaxRecords=1")
        mock_get_by_cid.assert_called_once_with(2244)

    @patch("local_app.lib.pub_chem.httpx")
    def test_search_no_results(self, mock_httpx) -> None:
        mock_httpx.get.return_value = _mock_httpx_json_response({})
        result = search("search_cid")
        assert [] == result
        mock_httpx.get.assert_called_once_with("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/search_cid/cids/JSON?MaxRecords=1")

    @patch("local_app.lib.pub_chem.httpx")
    def test_get_by_cid(self, mock_httpx) -> None:
        mock_httpx.get.side_effect = [
            _mock_httpx_json_response(_load_pubchem_json(_TEST_FILES_PATH / "compound.json")),
            _mock_httpx_json_response(_load_pubchem_json(_TEST_FILES_PATH / "synonyms.json")),
        ]
        result = get_by_cid("test_cid")
        assert {"cid": "test_cid",
                "molecularWeight": "180.16",
                "monoisotopic": "180.04225873",
                "name": "aspirin",
                "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"} == result
        mock_httpx.get.assert_has_calls([
            call("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/test_cid/JSON"),
            call("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/test_cid/synonyms/JSON"),
        ])

    def test_image_url(self) -> None:
        result = image_url("CID_1234")
        assert result == "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/CID_1234/PNG"


def _load_pubchem_json(file_path: Path) -> dict:
    assert file_path.is_file(), f"Missing pubchem JSON file at {file_path}"
    with file_path.open() as f:
        return json.loads(f.read())


def _mock_httpx_json_response(response_json: dict) -> Response:
    return Response(200, json=response_json)
