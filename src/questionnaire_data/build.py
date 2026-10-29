import hashlib
import json
from dataclasses import asdict, replace
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import seedcase_soil as so
import seedcase_sprout as sp
from pytask import DirectoryNode, Product, PythonNode, mark

from questionnaire_data import common, data, metadata

common.dotenv.load_env_vars()

SRC = Path(str(files("questionnaire_data"))).joinpath("..").resolve()
RAW = SRC.joinpath("..", "raw").resolve()
STAGING = SRC.joinpath("..", "staging").resolve()

RAW_DATA_PATH = RAW / "data"

FIELD_RESOURCE_MAPPING_PATH = (
    SRC / "questionnaire_data" / "metadata" / "redcap" / "mapping-field-to-resource.csv"
)

RAW_METADATA_PATH = RAW / "metadata" / "metadata.json"
STAGING_METADATA_PATH = STAGING / "metadata" / "metadata.json"

DATAPACKAGE_PATH = SRC.parent / "datapackage.json"


def _hash_properties(props: sp.SproutProperties) -> str:
    return hashlib.sha256(
        json.dumps(props.compact_dict, sort_keys=True).encode()
    ).hexdigest()


@mark.raw
def task_download_data(
    raw_data_path: Annotated[
        Path, DirectoryNode(root_dir=RAW_DATA_PATH, pattern="*.csv.gz"), Product
    ],
) -> None:
    """Download REDCap data to raw."""
    data_str = data.redcap.download()
    data.redcap.write(data_str, raw_data_path)


@mark.raw
def task_write_field_resource_mapping_csv(
    raw_data_paths: Annotated[
        list[Path], DirectoryNode(root_dir=RAW_DATA_PATH, pattern="*.csv.gz")
    ],
    mapping_csv_path: Annotated[Path, Product] = FIELD_RESOURCE_MAPPING_PATH,
):
    """Extract field names from newest raw and write to field resource mapping csv."""
    raw_data = data.redcap.read_newest_raw(raw_data_paths)
    # If new fields, append them to existing csv.
    data.redcap.write_columns_to_mapping_csv(raw_data, mapping_csv_path)


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
    so.write_properties(asdict(package_properties), datapackage_path)
