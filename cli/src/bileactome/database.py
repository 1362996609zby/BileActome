from __future__ import annotations

import json
from pathlib import Path

from .paths import default_database_dir
from .utils import atomic_write_json, sha256_file


DATABASE_VERSION = "2026.01"


def build_database_manifest(database_dir: Path | None = None) -> dict:
    database_dir = (database_dir or default_database_dir()).resolve()
    files = []
    for path in sorted(database_dir.glob("*.hmm")):
        files.append({"family": path.stem, "file": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "schema_version": "1.0",
        "database_name": "BileActome",
        "database_version": DATABASE_VERSION,
        "expected_family_count": 27,
        "files": files,
    }


def write_database_manifest(database_dir: Path | None = None, output: Path | None = None) -> Path:
    database_dir = (database_dir or default_database_dir()).resolve()
    output = output or database_dir.parent / "database_manifest.json"
    atomic_write_json(output, build_database_manifest(database_dir))
    return output


def load_manifest(database_dir: Path) -> tuple[Path, dict]:
    candidates = [database_dir / "database_manifest.json", database_dir.parent / "database_manifest.json"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Database manifest not found beside: {database_dir}")


def verify_database(database_dir: Path | None = None) -> dict:
    database_dir = (database_dir or default_database_dir()).expanduser().resolve()
    if not database_dir.is_dir():
        return {"ok": False, "database_dir": str(database_dir), "errors": ["database directory not found"], "files": []}
    try:
        manifest_path, expected = load_manifest(database_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return {"ok": False, "database_dir": str(database_dir), "errors": [str(exc)], "files": []}
    expected_by_name = {item["file"]: item for item in expected.get("files", [])}
    actual = {path.name: path for path in database_dir.glob("*.hmm")}
    checks = []
    errors = []
    for name, item in expected_by_name.items():
        path = actual.get(name)
        if path is None:
            checks.append({"file": name, "status": "missing"})
            errors.append(f"missing: {name}")
            continue
        digest = sha256_file(path)
        status = "pass" if digest == item["sha256"] else "checksum_mismatch"
        checks.append({"file": name, "status": status, "sha256": digest})
        if status != "pass":
            errors.append(f"checksum mismatch: {name}")
    extras = sorted(set(actual) - set(expected_by_name))
    if extras:
        errors.append("unexpected HMM files: " + ", ".join(extras))
    if len(expected_by_name) != expected.get("expected_family_count", 27):
        errors.append("manifest family count does not match expected_family_count")
    return {
        "ok": not errors,
        "database_dir": str(database_dir),
        "manifest": str(manifest_path),
        "database_version": expected.get("database_version"),
        "expected": expected.get("expected_family_count", 27),
        "passed": sum(item["status"] == "pass" for item in checks),
        "errors": errors,
        "files": checks,
    }

