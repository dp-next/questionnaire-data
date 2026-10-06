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


def write(data_str: str, raw_data_dir: Path) -> None:
    """Write REDCap data as a timestamped file."""
    df = pl.read_csv(StringIO(data_str), separator=";", infer_schema=False)
    raw_data_path = raw_data_dir / f"{common.datetime.get_current()}.csv.gz"
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    df.write_csv(raw_data_path, compression="gzip")
