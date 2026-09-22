from pathlib import Path
from typing import Any

import yaml12


def read(path: Path) -> Any:
    """Read a JSON file and return the data."""
    return yaml12.read_yaml(path)


def write(data: Any, path: Path) -> None:
    """Write data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    yaml12.write_yaml(data, path)
