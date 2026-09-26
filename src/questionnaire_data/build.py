import hashlib
import json
import tomllib
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import polars as pl
import seedcase_sprout as sp
from pytask import Product, PythonNode, mark

from questionnaire_data import common, metadata

common.dotenv.load_env_vars()

SRC = Path(str(files("questionnaire_data"))).joinpath("..").resolve()
RAW = SRC.joinpath("..", "raw").resolve()
STAGING = SRC.joinpath("..", "staging").resolve()

RAW_METADATA_PATH = RAW / "metadata" / "redcap.csv"
STAGING_METADATA_PATH = STAGING / "metadata" / "metadata.yaml"

DATAPACKAGE_PATH = SRC.parent / "datapackage.json"


def _hash_properties(props: sp.SproutProperties) -> str:
    return hashlib.sha256(
        json.dumps(props.compact_dict, sort_keys=True).encode()
    ).hexdigest()


@mark.persist
@mark.raw
def task_download_metadata(
    raw_metadata_path: Annotated[Path, Product] = RAW_METADATA_PATH,
) -> None:
    """Download the metadata to raw."""
    from_redcap = common.redcap.get_json("metadata")
    kept_fields = metadata.redcap.remove_unused_fields(from_redcap)
    metadata_df = pl.DataFrame(kept_fields)
    metadata_df.write_csv(raw_metadata_path)


@mark.metadata
def task_stage_metadata(
    staging_metadata_path: Annotated[Path, Product] = STAGING_METADATA_PATH,
    raw_metadata_path: Path = RAW_METADATA_PATH,
) -> None:
    """Prepare the REDCap metadata for transformation into datapackage.json."""
    metadata_dicts = pl.read_csv(raw_metadata_path).filter(pl.cols("form_names"))
    staged_metadata = metadata.redcap.stage_metadata(metadata_dicts)
    Path("test.toml").write_text(tomllib)

    common.yaml.write(staged_metadata, staging_metadata_path)


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
    staging_metadata = common.yaml.read(staging_metadata_path)
    resources = metadata.redcap.create_resource_properties(staging_metadata)
    package_properties = replace(package_properties, resources=resources)
    common.json.write(datapackage_path, package_properties.compact_dict)
