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


def read_newest_raw(raw_data_paths: list[Path]):
    """Read the newest downloaded raw data."""
    return pl.read_csv(
        # Newest data path based on datetime filename.
        max(raw_data_paths),
        infer_schema=False,
    )


def write_columns_to_mapping_csv(
    newest_raw_data: pl.DataFrame, mapping_csv_path: Path
) -> None:
    """Write raw data columns to CSV."""
    field_names = newest_raw_data.columns

    # If mapping csv exists, check for new fields and append them.
    if mapping_csv_path.exists():
        mapping_csv = pl.read_csv(mapping_csv_path, separator=";")
        existing_field_names = mapping_csv["field_name"].to_list()
        new_fields = [
            field_name
            for field_name in field_names
            if field_name not in existing_field_names
        ]
        if len(new_fields) != 0:
            pl.concat(
                [mapping_csv, pl.DataFrame({"field_name": new_fields})],
                # Fills in missing columns with None.
                how="diagonal",
            ).write_csv(mapping_csv_path, separator=";")

    else:
        pl.DataFrame({"field_name": field_names}).with_columns(
            new_field_name=pl.lit(None),
            resource_title=pl.lit(None),
            resource_name=pl.lit(None),
            comment=None,
        ).write_csv(mapping_csv_path, separator=";")
