from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from . import __version__
from .utils import atomic_write_json, utc_now


TOOLS = ("bash", "hmmsearch", "hmmscan", "hmmpress", "prodigal", "bowtie2", "bowtie2-build")
PYTHON_PACKAGES = ("biopython", "pandas", "numpy", "openpyxl")


def first_version_line(executable: str) -> str | None:
    path = shutil.which(executable)
    if not path:
        return None
    if executable in {"hmmsearch", "hmmscan", "hmmpress"}:
        candidates = ([path, "-h"],)
    elif executable == "prodigal":
        candidates = ([path, "-v"],)
    else:
        candidates = ([path, "--version"], [path, "-h"], [path, "-V"])
    for command in candidates:
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            continue
        text = (result.stdout + "\n" + result.stderr).strip()
        if text:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for line in lines:
                if "HMMER " in line or "Prodigal V" in line or " version " in line:
                    return line.lstrip("# ")
            return lines[0]
    return "version unavailable"


def environment_snapshot() -> dict:
    tools = {}
    for name in TOOLS:
        tools[name] = {"path": shutil.which(name), "version": first_version_line(name)}
    packages = {}
    for name in PYTHON_PACKAGES:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    return {
        "bileactome_version": __version__,
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "platform": platform.platform(),
        "tools": tools,
        "python_packages": packages,
    }


def create_manifest(project_dir: Path, workflow: str, parameters: dict, inputs: dict) -> dict:
    return {
        "schema_version": "1.0",
        "workflow": workflow,
        "status": "running",
        "started_at": utc_now(),
        "completed_at": None,
        "environment": environment_snapshot(),
        "parameters": parameters,
        "inputs": inputs,
        "steps": {},
        "outputs": [],
        "project_dir": str(project_dir),
    }


def save_manifest(project_dir: Path, manifest: dict) -> Path:
    path = project_dir / "run_manifest.json"
    atomic_write_json(path, manifest)
    return path


def set_step(manifest: dict, name: str, status: str, detail: str = "") -> None:
    manifest["steps"][name] = {"status": status, "detail": detail, "updated_at": utc_now()}


def finalize_manifest(project_dir: Path, manifest: dict, status: str) -> None:
    manifest["status"] = status
    manifest["completed_at"] = utc_now()
    manifest["outputs"] = [
        str(path.relative_to(project_dir))
        for path in sorted(project_dir.rglob("*"))
        if path.is_file() and path.name != "run_manifest.json"
    ]
    save_manifest(project_dir, manifest)
