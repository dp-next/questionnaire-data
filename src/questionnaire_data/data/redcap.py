from io import StringIO
from pathlib import Path

import polars as pl

from questionnaire_data import common


def download() -> str:
    """Download REDCap data."""
    return common.redcap.get(
        request_data={
            "content": "record",
            "action": "export",
            "format": "csv",
            "type": "flat",
            "csvDelimiter": ";",
            "rawOrLabel": "raw",
            "rawOrLabelHeaders": "raw",
            "exportCheckboxLabel": "false",
            "exportSurveyFields": "false",
            "exportDataAccessGroups": "false",
            "returnFormat": "json",
        }
    ).text


def write(data_str: str, raw_data_path: Path) -> None:
    """Write REDCap data as a timestamped file."""
    df = pl.read_csv(StringIO(data_str), separator=";", infer_schema=False)
    raw_data_path = raw_data_path / f"{common.datetime.get_current()}.csv.gz"
    raw_data_path.mkdir(parents=True, exist_ok=True)
    df.write_csv(raw_data_path, compression="gzip")


def read_newest_raw(raw_data_paths: Path):
    """Read the newest downloaded raw data."""
    return pl.read_csv(
        # Newest data path based on datetime filename.
        max(raw_data_paths),
        infer_schema=False,
    )

