from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile


@dataclass
class PackageSummary:
    package_path: Path
    files: list[str]
    has_etp_db: bool
    has_graphics_zip: bool


class OfflinePackageReader:
    def inspect(self, package_path: Path) -> PackageSummary:
        if not package_path.exists():
            raise FileNotFoundError(package_path)

        with zipfile.ZipFile(package_path) as archive:
            files = archive.namelist()

        return PackageSummary(
            package_path=package_path,
            files=files,
            has_etp_db=any(Path(name).name == "etp.db" for name in files),
            has_graphics_zip=any(Path(name).name == "graphics.zip" for name in files),
        )
