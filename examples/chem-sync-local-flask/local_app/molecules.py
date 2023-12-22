import logging
from typing import Any

from benchling_sdk.apps.framework import App
from benchling_sdk.helpers.serialization_helpers import fields
from benchling_sdk.models import (
    Molecule,
    MoleculeCreate,
    MoleculeStructure,
    MoleculeStructureStructureFormat,
)

logger = logging.getLogger(__name__)


def create_molecule(app: App, chemical_result: dict[str, Any]) -> Molecule:
    logger.debug("Chemical to create: %s", chemical_result)
    molecule_structure = MoleculeStructure(
        structure_format=MoleculeStructureStructureFormat.SMILES,
        value=chemical_result["smiles"],
    )
    config = app.config_store.config_by_path
    molecular_weight_field = config(["Molecule Schema", "Molecular Weight"]).required().value_str()
    mono_isotopic_field = config(["Molecule Schema", "MonoIsotopic"]).required().value_str()
    molecule_create = MoleculeCreate(
        chemical_structure=molecule_structure,
        name=chemical_result["name"],
        aliases=[f"cid:{chemical_result['cid']}"],
        folder_id=config(["Sync Folder"]).required().value_str(),
        schema_id=config(["Molecule Schema"]).required().value_str(),
        fields=fields(
            {
                molecular_weight_field: {"value": chemical_result["molecularWeight"]},
                mono_isotopic_field: {"value": chemical_result["monoisotopic"]},
            }
        ),
    )
    return app.benchling.molecules.create(molecule_create)
