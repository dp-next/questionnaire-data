import hashlib
import json
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import polars as pl
import seedcase_soil as so
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


@mark.skipif(
    common.redcap.is_empty_env(), reason="API env key is not present, so skipping."
)
@mark.raw
def task_download_metadata(
    raw_metadata_path: Annotated[Path, Product] = RAW_METADATA_PATH,
) -> None:
    """Download the metadata to raw."""
    from_redcap = common.redcap.get_json("metadata")
    kept_fields = so.fmap(from_redcap, metadata.redcap.remove_unused_fields)
    metadata_df = pl.DataFrame(kept_fields)
    kept_forms = metadata.redcap.keep_needed_forms(metadata_df)
    renamed_forms = metadata.redcap.rename_forms(kept_forms)
    renamed_forms.write_csv(raw_metadata_path)


@mark.metadata
def task_stage_metadata(
    staging_metadata_path: Annotated[Path, Product] = STAGING_METADATA_PATH,
    raw_metadata_path: Path = RAW_METADATA_PATH,
) -> None:
    """Prepare the REDCap metadata for transformation into datapackage.json."""
    metadata_df = pl.read_csv(raw_metadata_path)
    # staged_metadata = metadata.redcap.stage_metadata(metadata_dicts)

    common.yaml.write(kept_forms, staging_metadata_path)


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
