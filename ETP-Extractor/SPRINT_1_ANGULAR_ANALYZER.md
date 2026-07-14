from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def export_rows(rows: Iterable[dict], output_path: Path) -> None:
    rows = list(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
