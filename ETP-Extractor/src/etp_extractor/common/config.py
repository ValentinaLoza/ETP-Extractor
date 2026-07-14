from __future__ import annotations

import json
from pathlib import Path


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
