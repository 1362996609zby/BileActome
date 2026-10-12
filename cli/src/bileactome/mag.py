from __future__ import annotations

import csv
import logging
import shutil
from collections import defaultdict
from pathlib import Path

from .database import verify_database
from .manifest import create_manifest, finalize_manifest, save_manifest, set_step
from .paths import default_database_dir
from .utils import ensure_output_dir, nonempty, run_command, setup_logging


def parse_tblout(path: Path, evalue: float) -> set[str]:
    hits = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 5:
                continue
            try:
                value = float(fields[4])
            except ValueError:
                continue
            if value <= evalue:
                hits.add(fields[0])
    return hits


def fasta_records(path: Path):
    header = None
    sequence = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    yield header, sequence
                header, sequence = line, []
            else:
                sequence.append(line)
        if header is not None:
            yield header, sequence


def extract_hits(protein: Path, hit_ids: set[str], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    count = 0
    with temporary.open("w", encoding="utf-8") as out:
        for header, sequence in fasta_records(protein):
            if header[1:].split(None, 1)[0] in hit_ids:
                out.write(header + "\n" + "\n".join(sequence) + "\n")
                count += 1
    temporary.replace(output)
    return count


def write_count_matrix(output_dir: Path, evalue: float) -> Path:
    tbl_files = sorted(output_dir.glob("hmmsearch/*/*.tbl"))
    matrix: dict[str, dict[str, int]] = defaultdict(dict)
    genomes, families = set(), set()
    for path in tbl_files:
        family, genome = path.parent.name, path.stem
        genomes.add(genome)
        families.add(family)
        matrix[genome][family] = len(parse_tblout(path, evalue))
    out = output_dir / f"hmmsearch_counts_E{evalue:.0e}.tsv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        ordered = sorted(families)
        writer.writerow(["Genome"] + ordered)
        for genome in sorted(genomes):
            writer.writerow([genome] + [matrix[genome].get(family, 0) for family in ordered])
    return out


def run_mag(genome_dir: Path, output_dir: Path, database_dir: Path | None = None, threads: int = 1, evalue: float = 1e-3, prodigal_mode: str = "meta", extract: bool = True, force: bool = False, verbose: bool = False) -> Path:
    if threads < 1 or evalue <= 0:
        raise ValueError("threads must be >= 1 and evalue must be > 0")
    genome_dir = genome_dir.expanduser().resolve()
    if not genome_dir.is_dir():
        raise ValueError(f"Genome directory not found: {genome_dir}")
    genomes = [p for p in sorted(genome_dir.iterdir()) if p.is_file() and p.suffix.lower() in {".fna", ".fa", ".fasta"} and p.stat().st_size > 0]
    if not genomes:
        raise ValueError(f"No non-empty genome FASTA files found: {genome_dir}")
    stems = [p.stem for p in genomes]
    if len(stems) != len(set(stems)):
        raise ValueError("Duplicated genome IDs after removing FASTA suffixes")
    database_dir = (database_dir or default_database_dir()).expanduser().resolve()
    db_report = verify_database(database_dir)
    if not db_report["ok"]:
        raise ValueError("Database verification failed: " + "; ".join(db_report["errors"]))
    for executable in ("prodigal", "hmmsearch"):
        if not shutil.which(executable):
            raise RuntimeError(f"Required executable not found in PATH: {executable}")
    output_dir = ensure_output_dir(output_dir)
    logger = setup_logging(output_dir / "bileactome_mag.log", verbose)
    parameters = {"threads": threads, "evalue": evalue, "prodigal_mode": prodigal_mode, "extract_hits": extract, "force": force}
    inputs = {"genome_dir": str(genome_dir), "genomes": [str(p) for p in genomes], "database_dir": str(database_dir), "database_version": db_report["database_version"]}
    manifest = create_manifest(output_dir, "mag_wgs", parameters, inputs)
    save_manifest(output_dir, manifest)
    proteins = output_dir / "proteins"
    searches = output_dir / "hmmsearch"
    proteins.mkdir(exist_ok=True)
    searches.mkdir(exist_ok=True)
    try:
        set_step(manifest, "predict_proteins", "running")
        save_manifest(output_dir, manifest)
        for genome in genomes:
            protein = proteins / f"{genome.stem}.faa"
            if nonempty(protein) and not force:
                logger.info("Skip existing protein file: %s", protein)
                continue
            run_command(["prodigal", "-i", str(genome), "-a", str(protein), "-p", prodigal_mode, "-q"], logger)
            if not nonempty(protein):
                raise RuntimeError(f"Prodigal produced no protein sequences: {protein}")
        set_step(manifest, "predict_proteins", "completed")
        set_step(manifest, "hmmsearch", "running")
        save_manifest(output_dir, manifest)
        for hmm in sorted(database_dir.glob("*.hmm")):
            family_dir = searches / hmm.stem
            family_dir.mkdir(parents=True, exist_ok=True)
            for genome in genomes:
                protein = proteins / f"{genome.stem}.faa"
                tbl = family_dir / f"{genome.stem}.tbl"
                stdout = family_dir / f"{genome.stem}.txt"
                if nonempty(tbl) and not force:
                    logger.info("Skip existing HMMER table: %s", tbl)
                    continue
                run_command(["hmmsearch", "--cpu", str(threads), "--tblout", str(tbl), "-o", str(stdout), str(hmm), str(protein)], logger)
        set_step(manifest, "hmmsearch", "completed")
        if extract:
            set_step(manifest, "extract_hits", "running")
            for tbl in sorted(searches.glob("*/*.tbl")):
                protein = proteins / f"{tbl.stem}.faa"
                output = tbl.parent / "hits" / f"{tbl.stem}_hits.fasta"
                if nonempty(output) and not force:
                    continue
                extract_hits(protein, parse_tblout(tbl, evalue), output)
            set_step(manifest, "extract_hits", "completed")
        matrix = write_count_matrix(output_dir, evalue)
        set_step(manifest, "count_matrix", "completed", str(matrix))
        finalize_manifest(output_dir, manifest, "completed")
        logger.info("MAG/WGS workflow completed: %s", matrix)
        return matrix
    except Exception as exc:
        logger.exception("MAG/WGS workflow failed")
        set_step(manifest, "failure", "failed", str(exc))
        finalize_manifest(output_dir, manifest, "failed")
        raise

