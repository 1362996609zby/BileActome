from __future__ import annotations

import tempfile
from pathlib import Path

from .doctor import diagnose
from .paths import package_root


def locate_fixture(explicit: Path | None = None) -> Path:
    if explicit:
        return explicit.expanduser().resolve()
    candidates = [package_root() / "data" / "toy" / "toy_gene_catalog", Path.cwd() / "tests" / "fixtures" / "toy_gene_catalog", Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "toy_gene_catalog"]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Toy gene-catalog fixture not found; use --fixture-dir")


def locate_mag_fixture(catalog_fixture: Path) -> Path:
    candidates = [
        catalog_fixture.parent / "toy_mag",
        Path.cwd() / "tests" / "fixtures" / "toy_mag",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Toy MAG fixture not found beside the gene-catalog fixture")


def run_selftest(workflow: str = "all", fixture_dir: Path | None = None, output_dir: Path | None = None, threads: int = 2) -> dict:
    from .catalog import run_catalog
    from .mag import run_mag
    from .validation import validate_project

    if workflow not in {"mag", "catalog", "all"}:
        raise ValueError("workflow must be mag, catalog, or all")
    health = diagnose(workflow=workflow)
    if not health["ok"]:
        return {"ok": False, "stage": "doctor", "doctor": health}
    fixture = locate_fixture(fixture_dir)
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="bileactome-selftest-"))
    output_dir = output_dir.expanduser().resolve()
    reports = {}
    if workflow in {"mag", "all"}:
        mag_project = output_dir / "mag"
        run_mag(locate_mag_fixture(fixture), mag_project, threads=threads)
        reports["mag"] = validate_project(mag_project)
    if workflow in {"catalog", "all"}:
        catalog_project = output_dir / "catalog"
        run_catalog(
            protein_fasta=fixture / "gene_catalog" / "toy_unigenes.protein.fa",
            cds_fasta=fixture / "gene_catalog" / "toy_unigenes.CDS.fa",
            reads_dir=fixture / "clean_reads",
            output_dir=catalog_project,
            threads=threads,
        )
        reports["catalog"] = validate_project(catalog_project)
    return {
        "ok": all(report["ok"] for report in reports.values()),
        "workflow": workflow,
        "output_dir": str(output_dir),
        "validations": reports,
    }
