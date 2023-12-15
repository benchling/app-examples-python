from typing import Any, cast

from benchling_sdk.apps.framework import App
from benchling_sdk.helpers.serialization_helpers import fields
from benchling_sdk.models import (
    Molecule,
    MoleculeCreate,
    MoleculeStructure,
    MoleculeStructureStructureFormat,
)
from flask import current_app


def create_molecule(app: App, chemical_result: dict[str, Any]) -> Molecule:
    current_app.logger.debug("Chemical to create: %s", chemical_result)
    molecule_structure = MoleculeStructure(
        structure_format=MoleculeStructureStructureFormat.SMILES,
        value=chemical_result["smiles"],
    )
    molecular_weight_field = _config_value(app, ["Molecule Schema", "Molecular Weight"])
    mono_isotopic_field = _config_value(app, ["Molecule Schema", "MonoIsotopic"])
    molecule_create = MoleculeCreate(
        chemical_structure=molecule_structure,
        name=chemical_result["name"],
        aliases=[f"cid:{chemical_result['cid']}"],
        folder_id=_config_value(app, ["Sync Folder"]),
        schema_id=_config_value(app, ["Molecule Schema"]),
        fields=fields(
            {
                molecular_weight_field: {"value": chemical_result["molecularWeight"]},
                mono_isotopic_field: {"value": chemical_result["monoisotopic"]},
            }
        ),
    )
    return app.benchling.molecules.create(molecule_create)


# Only needed if you care about type safety.
# For this App, all our config items happen to be required and strings
def _config_value(app: App, path: list[str]) -> str:
    config_item = app.config_store.config_by_path(path)
    assert config_item is not None, f"Missing required config item for {path}"
    assert config_item.value is not None, f"Missing required config item value for {path}"
    return cast(str, config_item.value)
