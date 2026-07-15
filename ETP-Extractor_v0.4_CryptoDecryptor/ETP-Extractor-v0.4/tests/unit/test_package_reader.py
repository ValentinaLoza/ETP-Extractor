from pathlib import Path
import zipfile

from etp_extractor.package_reader.reader import OfflinePackageReader


def test_inspects_package(tmp_path: Path) -> None:
    package = tmp_path / "sample.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("etp.db/CURRENT", "MANIFEST")
        archive.writestr("graphics.zip", b"")

    summary = OfflinePackageReader().inspect(package)

    assert summary.has_etp_db
    assert summary.has_graphics_zip
