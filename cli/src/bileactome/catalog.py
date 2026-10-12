from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .database import verify_database
from .manifest import create_manifest, finalize_manifest, save_manifest, set_step
from .paths import default_database_dir, legacy_catalog_dir
from .utils import ensure_output_dir, nonempty, require_dir, require_file, run_command, setup_logging


def _script(name: str) -> Path:
    path = legacy_catalog_dir() / name
    if not path.is_file():
        raise RuntimeError(f"Packaged workflow script not found: {path}")
    return path


def _require_tools() -> None:
    for executable in ("bash", "hmmscan", "hmmpress", "bowtie2", "bowtie2-build"):
        if not shutil.which(executable):
            raise RuntimeError(f"Required executable not found in PATH: {executable}")


def run_catalog(
    protein_fasta: Path,
    cds_fasta: Path,
    reads_dir: Path,
    output_dir: Path,
    database_dir: Path | None = None,
    threads: int = 8,
    evalue: float = 1e-3,
    dom_evalue: float = 1e-3,
    epsilon: float = 1e-12,
    id_regex: str | None = None,
    force: bool = False,
    verbose: bool = False,
) -> Path:
    if threads < 1 or min(evalue, dom_evalue, epsilon) <= 0:
        raise ValueError("threads must be >= 1; evalue, dom-evalue and epsilon must be > 0")
    protein_fasta = require_file(protein_fasta, "Protein catalog")
    cds_fasta = require_file(cds_fasta, "CDS catalog")
    reads_dir = require_dir(reads_dir, "Clean reads")
    database_dir = (database_dir or default_database_dir()).expanduser().resolve()
    db_report = verify_database(database_dir)
    if not db_report["ok"]:
        raise ValueError("Database verification failed: " + "; ".join(db_report["errors"]))
    _require_tools()
    output_dir = ensure_output_dir(output_dir)
    logger = setup_logging(output_dir / "bileactome_catalog.log", verbose)
    parameters = {"threads": threads, "evalue": evalue, "dom_evalue": dom_evalue, "epsilon": epsilon, "id_regex": id_regex, "force": force}
    inputs = {"protein_fasta": str(protein_fasta), "cds_fasta": str(cds_fasta), "reads_dir": str(reads_dir), "database_dir": str(database_dir), "database_version": db_report["database_version"]}
    manifest = create_manifest(output_dir, "non_redundant_gene_catalog", parameters, inputs)
    save_manifest(output_dir, manifest)

    hmm_results = output_dir / "01_hmm_results"
    working_database = output_dir / "00_working_database"
    target_dir = output_dir / "02_target_cds"
    mapping_dir = output_dir / "03_bowtie2_map"
    abundance_dir = output_dir / "04_gene_abundance"
    results_dir = output_dir / "05_results"
    for directory in (working_database, hmm_results, target_dir, mapping_dir, abundance_dir, results_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for source_hmm in sorted(database_dir.glob("*.hmm")):
        target_hmm = working_database / source_hmm.name
        if not target_hmm.exists() or target_hmm.stat().st_size != source_hmm.stat().st_size:
            shutil.copy2(source_hmm, target_hmm)
    target_cds = target_dir / "target_cds.fa"
    function_map = target_dir / "gene_to_function.tsv"
    merged_xlsx = results_dir / "abundance_merged_with_function.xlsx"
    merged_tsv = results_dir / "abundance_merged_with_function.tsv"
    function_sum = results_dir / "FunctionSum_matrix.xlsx"
    relative = results_dir / "Relative_abundance_matrix.xlsx"
    clr = results_dir / "CLR_matrix.xlsx"

    try:
        set_step(manifest, "hmm_annotation", "running")
        save_manifest(output_dir, manifest)
        command = ["bash", str(_script("step1_hmm_annotation.sh")), "--protein-fasta", str(protein_fasta), "--hmm-dir", str(working_database), "--out-dir", str(hmm_results), "--cpu", str(threads), "--evalue", str(evalue), "--dom-evalue", str(dom_evalue)]
        if force:
            command.append("--force")
        run_command(command, logger)
        set_step(manifest, "hmm_annotation", "completed")

        set_step(manifest, "extract_cds", "running")
        command = [sys.executable, str(_script("step2_extract_matched_cds.py")), "--hmm-result-dir", str(hmm_results), "--cds-fasta", str(cds_fasta), "--out-cds", str(target_cds), "--out-map", str(function_map)]
        if id_regex:
            command.extend(["--id-regex", id_regex])
        if force:
            command.append("--force")
        if not (nonempty(target_cds) and nonempty(function_map)) or force:
            run_command(command, logger)
        else:
            logger.info("Skip existing target CDS and function map")
        set_step(manifest, "extract_cds", "completed")

        set_step(manifest, "bowtie2_mapping", "running")
        command = ["bash", str(_script("step3_bowtie2_mapping.sh")), "--target-cds", str(target_cds), "--reads-dir", str(reads_dir), "--out-dir", str(mapping_dir), "--threads", str(threads)]
        if force:
            command.append("--force")
        run_command(command, logger)
        set_step(manifest, "bowtie2_mapping", "completed")

        set_step(manifest, "rpkm", "running")
        command = [sys.executable, str(_script("step4_abundance_calc.py")), "--sam-dir", str(mapping_dir), "--cds-fasta", str(target_cds), "--out-dir", str(abundance_dir)]
        if id_regex:
            command.extend(["--id-regex", id_regex])
        if force:
            command.append("--force")
        run_command(command, logger)
        set_step(manifest, "rpkm", "completed")

        set_step(manifest, "merge_abundance", "running")
        command = [sys.executable, str(_script("step5_merge_abundance_with_function.py")), "--abundance-dir", str(abundance_dir), "--function-map", str(function_map), "--out-xlsx", str(merged_xlsx), "--out-tsv", str(merged_tsv)]
        if force:
            command.append("--force")
        if not nonempty(merged_xlsx) or force:
            run_command(command, logger)
        else:
            logger.info("Skip existing merged abundance matrix")
        set_step(manifest, "merge_abundance", "completed")

        set_step(manifest, "family_matrices", "running")
        command = [sys.executable, str(_script("step6_function_abundance_transform.py")), "--in-table", str(merged_xlsx), "--out-func", str(function_sum), "--out-rel", str(relative), "--out-clr", str(clr), "--epsilon", str(epsilon)]
        if force:
            command.append("--force")
        if not all(nonempty(path) for path in (function_sum, relative, clr)) or force:
            run_command(command, logger)
        else:
            logger.info("Skip existing family abundance matrices")
        set_step(manifest, "family_matrices", "completed")
        finalize_manifest(output_dir, manifest, "completed")
        logger.info("Gene-catalog workflow completed: %s", results_dir)
        return results_dir
    except Exception as exc:
        logger.exception("Gene-catalog workflow failed")
        set_step(manifest, "failure", "failed", str(exc))
        finalize_manifest(output_dir, manifest, "failed")
        raise
