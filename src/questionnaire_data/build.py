import hashlib
import json
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import seedcase_sprout as sp
from pytask import Product, PythonNode, mark

from questionnaire_data import common, metadata

common.dotenv.load_env_vars()

SRC = Path(str(files("questionnaire_data"))).joinpath("..").resolve()
RAW = SRC.joinpath("..", "raw").resolve()
STAGING = SRC.joinpath("..", "staging").resolve()

RAW_METADATA_PATH = RAW / "metadata" / "metadata.json"
STAGING_METADATA_PATH = STAGING / "metadata" / "metadata.json"

DATAPACKAGE_PATH = SRC.parent / "datapackage.json"


def _hash_properties(props: sp.SproutProperties) -> str:
    return hashlib.sha256(
        json.dumps(props.compact_dict, sort_keys=True).encode()
    ).hexdigest()


@mark.metadata
def task_download_metadata(
    raw_metadata_path: Annotated[Path, Product] = RAW_METADATA_PATH,
) -> None:
    """Download the metadata to raw."""
    redcap_metadata = common.redcap.get_json("metadata")
    common.json.write(raw_metadata_path, redcap_metadata)


@mark.metadata
def task_stage_metadata(
    staging_metadata_path: Annotated[Path, Product] = STAGING_METADATA_PATH,
    raw_metadata_path: Path = RAW_METADATA_PATH,
) -> None:
    """Prepare the REDCap metadata for transformation into datapackage.json."""
    raw_metadata = common.json.read(raw_metadata_path)
    staged_metadata = metadata.redcap.stage_metadata(raw_metadata)
    common.json.write(staging_metadata_path, staged_metadata)


@mark.metadata
def task_create_datapackage_json(
    package_properties: Annotated[
        sp.SproutProperties,
        # `SproutProperties` is a mutable dataclass, so it has no `__hash__`;
        # `_hash_properties` gives Pytask a stable content hash to detect changes.
        PythonNode(value=metadata.package.package_properties, hash=_hash_properties),
    ],
    datapackage_path: Annotated[Path, Product] = DATAPACKAGE_PATH,
    staging_metadata_path: Path = STAGING_METADATA_PATH,
) -> None:
    """Create the datapackage.json file from the REDCap metadata."""
    staging_metadata = common.json.read(staging_metadata_path)
    resources = metadata.redcap.create_resource_properties(staging_metadata)
    package_properties = replace(package_properties, resources=resources)
    sp.write_properties(package_properties, datapackage_path)
