from pathlib import Path
from unittest.mock import MagicMock

from benchling_sdk.apps.config.mock_config import MockConfigItemStore
from benchling_sdk.apps.framework import App
from benchling_sdk.apps.helpers.manifest_helpers import manifest_from_file
from benchling_sdk.helpers.serialization_helpers import fields
from benchling_sdk.models import (
    GenericApiIdentifiedAppConfigItem,
    GenericApiIdentifiedAppConfigItemType,
    Molecule,
    MoleculeCreate,
    MoleculeStructure,
    MoleculeStructureStructureFormat,
)

from local_app.benchling_app.molecules import create_molecule


class TestMolecules:
    def test_create_molecule(self) -> None:
        # Setup mocks
        app = MagicMock(App)
        manifest = manifest_from_file(Path(__file__).parent.parent.parent.parent.parent / "manifest.yaml")
        # This will mock all config items with random valid values
        # We can override particular configs if desired. This shows an example of overriding a folder config
        mock_config_store = MockConfigItemStore.from_manifest(manifest).with_replacement(
            GenericApiIdentifiedAppConfigItem(
                path=["Sync Folder"],
                value="set_folder_id",
                type=GenericApiIdentifiedAppConfigItemType.FOLDER),
        )
        app.config_store = mock_config_store
        chemical_result = {
            "cid": "cid_value",
            "smiles": "smiles_value",
            "name": "chemical_name",
            "molecularWeight": 0.123,
            "monoisotopic": 1.456,
        }
        mock_molecule = MagicMock(Molecule)
        app.benchling.molecules.create.return_value = mock_molecule

        # Expected values
        molecule_structure = MoleculeStructure(
            structure_format=MoleculeStructureStructureFormat.SMILES,
            value="smiles_value",
        )
        # These are generated as random valid values unless manually overridden
        # Since we didn't override them but we're verifying the entire MoleculeCreate stub for correctness,
        # pull the mocked values from the mock_config_store
        weight_field_config_value = mock_config_store\
            .config_by_path(["Molecule Schema", "Molecular Weight"])\
            .required().value_str()
        mono_isotopic_field_config_value = mock_config_store\
            .config_by_path(["Molecule Schema", "MonoIsotopic"])\
            .required().value_str()
        schema_id = mock_config_store.config_by_path(["Molecule Schema"]).required().value_str()
        expected_argument = MoleculeCreate(
            chemical_structure=molecule_structure,
            name="chemical_name",
            aliases=["cid:cid_value"],
            # We manually set this one instead of a random mocked value, as an example
            folder_id="set_folder_id",
            schema_id=schema_id,
            fields=fields(
                {
                    weight_field_config_value: {"value": 0.123},
                    mono_isotopic_field_config_value: {"value": 1.456},
                },
            ),
        )

        # Verify
        result = create_molecule(app, chemical_result)
        assert mock_molecule == result
        app.benchling.molecules.create.assert_called_once_with(expected_argument)
