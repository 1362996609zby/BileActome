from __future__ import annotations

import hashlib
import json
import logging
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def require_file(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if not nonempty(path):
        raise ValueError(f"{label} not found or empty: {path}")
    return path


def require_dir(path: Path, label: str) -> Path:
    path = path.expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"{label} directory not found: {path}")
    return path


def ensure_output_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".bileactome_write_test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        raise ValueError(f"Output directory is not writable: {path}: {exc}") from exc
    return path


def setup_logging(log_file: Path, verbose: bool = False) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"bileactome.{log_file.parent.name}")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(stream)
    logger.addHandler(file_handler)
    return logger


def display_command(command: Iterable[object]) -> str:
    return shlex.join([str(item) for item in command])


def run_command(command: list[str], logger: logging.Logger, cwd: Path | None = None) -> None:
    logger.info("CMD: %s", display_command(command))
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.stdout.strip():
        logger.info(result.stdout.rstrip())
    if result.stderr.strip():
        (logger.error if result.returncode else logger.info)(result.stderr.rstrip())
    if result.returncode:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {display_command(command)}")


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)

