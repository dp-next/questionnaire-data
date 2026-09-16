import json
from pathlib import Path
from typing import Any


def read(path: Path) -> Any:
    """Read a JSON file and return the data."""
    with open(path) as f:
        return json.load(f)


def write(path: Path, data: Any) -> None:
    """Write data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
