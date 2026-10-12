from __future__ import annotations

import json
import platform
import re
from pathlib import Path

from .database import verify_database
from .manifest import environment_snapshot
from .utils import atomic_write_json


def supported_tool_version(name: str, value: str | None) -> bool | None:
    if not value:
        return None
    match = re.search(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        return None
    detected = tuple(int(part or 0) for part in match.groups())
    if name == "bash":
        return detected >= (4, 0, 0)
    if name in {"hmmsearch", "hmmscan", "hmmpress"}:
        return (3, 4, 0) <= detected < (3, 5, 0)
    if name == "prodigal":
        return (2, 6, 3) <= detected < (2, 7, 0)
    if name in {"bowtie2", "bowtie2-build"}:
        return (2, 5, 4) <= detected < (2, 6, 0)
    return None


def diagnose(database_dir: Path | None = None, workflow: str = "all") -> dict:
    env = environment_snapshot()
    required_tools = {"all": ["bash", "hmmsearch", "hmmscan", "hmmpress", "prodigal", "bowtie2", "bowtie2-build"], "mag": ["hmmsearch", "prodigal"], "catalog": ["bash", "hmmscan", "hmmpress", "bowtie2", "bowtie2-build"]}[workflow]
    checks = []
    checks.append({"component": "platform", "status": "PASS" if platform.system() == "Linux" else "WARNING", "detail": platform.platform()})
    python_pair = tuple(int(item) for item in platform.python_version_tuple()[:2])
    py_ok = (3, 10) <= python_pair < (3, 13)
    checks.append({"component": "python", "status": "PASS" if py_ok else "FAIL", "detail": env["python"]})
    for name in required_tools:
        item = env["tools"][name]
        compatible = supported_tool_version(name, item["version"])
        status = "FAIL" if not item["path"] or compatible is False else ("PASS" if compatible else "WARNING")
        checks.append({"component": name, "status": status, "detail": {**item, "supported_version": compatible}})
    for name, detected in env["python_packages"].items():
        checks.append({"component": name, "status": "PASS" if detected else "FAIL", "detail": detected})
    database = verify_database(database_dir)
    checks.append({"component": "BileActome database", "status": "PASS" if database["ok"] else "FAIL", "detail": {"passed": database.get("passed"), "expected": database.get("expected"), "version": database.get("database_version"), "errors": database.get("errors")}})
    ok = all(item["status"] != "FAIL" for item in checks)
    return {"ok": ok, "workflow": workflow, "checks": checks, "environment": env, "database": database}


def print_diagnosis(report: dict) -> None:
    for item in report["checks"]:
        print(f"[{item['status']}] {item['component']}: {json.dumps(item['detail'], ensure_ascii=False)}")
    print("Environment is ready." if report["ok"] else "Environment has blocking failures.")


def write_report(report: dict, path: Path) -> None:
    atomic_write_json(path.expanduser().resolve(), report)
