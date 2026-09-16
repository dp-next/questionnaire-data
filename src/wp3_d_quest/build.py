import hashlib
import json
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import seedcase_sprout as sp
from pytask import Product, PythonNode, mark

from wp3_d_quest import common, metadata

common.dotenv.load_env_vars()

SRC = Path(str(files("wp3_d_quest"))).joinpath("..").resolve()
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
    datapackage_path: Annotated[Path, Product] = DATAPACKAGE_PATH,
    staging_metadata_path: Path = STAGING_METADATA_PATH,
    package_properties: Annotated[
        sp.SproutProperties, PythonNode(hash=_hash_properties)
    ] = metadata.package.package_properties,
) -> None:
    """Create the datapackage.json file from the REDCap metadata."""
    staging_metadata = common.json.read(staging_metadata_path)
    resources = metadata.redcap.create_resource_properties(staging_metadata)
    package_properties = replace(package_properties, resources=resources)
    common.json.write(datapackage_path, package_properties.compact_dict)
