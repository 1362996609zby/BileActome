from importlib.resources import files
from pathlib import Path


def package_root() -> Path:
    return Path(str(files("bileactome")))


def default_database_dir() -> Path:
    return package_root() / "data" / "hmm"


def legacy_mag_dir() -> Path:
    return package_root() / "legacy" / "mag"


def legacy_catalog_dir() -> Path:
    return package_root() / "legacy" / "catalog"

