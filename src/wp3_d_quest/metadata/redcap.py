from typing import Any


def create_datapackage(metadata: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a datapackage.json file from the REDCap metadata."""
    return metadata[0]
