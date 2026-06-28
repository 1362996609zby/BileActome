#!/usr/bin/env python3
"""Run the BileActome MAG/WGS HMM search workflow.

This script predicts proteins from genome FASTA files once with Prodigal and
then searches the same protein files against every BileActome HMM profile in a
directory. Existing non-empty outputs are skipped by default, so interrupted
runs can be resumed safely.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Predict MAG/WGS proteins once with Prodigal and run hmmsearch "
            "against all .hmm files in a BileActome HMM directory."
        )
    )
    parser.add_argument(
        "--genome-dir",
        required=True,
        type=Path,
        help="Directory containing genome/MAG nucleotide FASTA files.",
    )
    parser.add_argument(
        "--hmm-dir",
        required=True,
        type=Path,
        help="Directory containing BileActome .hmm files.",
    )
    parser.add_argument(
        "--protein-dir",
        type=Path,
        default=None,
        help="Directory for Prodigal-predicted proteins. Default: <genome-dir>/AA.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("bileactome_mag_wgs_results"),
        help="Output directory for family-specific hmmsearch results.",
    )
    parser.add_argument(
        "--genome-suffixes",
        default=".fna,.fa,.fasta",
        help="Comma-separated genome FASTA suffixes to include. Default: .fna,.fa,.fasta.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="CPU threads passed to hmmsearch and Prodigal where supported. Default: 1.",
    )
    parser.add_argument(
        "--prodigal-mode",
        default="meta",
        choices=["meta", "single"],
        help="Prodigal mode. Use 'meta' for MAGs/metagenomic contigs. Default: meta.",
    )
    parser.add_argument(
        "--force-prodigal",
        action="store_true",
        help="Regenerate protein FASTA files even if non-empty .faa files already exist.",
    )
    parser.add_argument(
        "--force-hmmsearch",
        action="store_true",
        help="Regenerate hmmsearch .tbl files even if non-empty outputs already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands without running Prodigal or hmmsearch.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Optional log file. Default: <output-dir>/run_hmmsearch_batch.log.",
    )
    return parser.parse_args()


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        ],
    )


def check_executable(name: str, dry_run: bool = False) -> None:
    if dry_run:
        return
    if shutil.which(name) is None:
        raise SystemExit(f"Required executable not found in PATH: {name}")


def nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def run_command(cmd: list[str], dry_run: bool = False) -> None:
    logging.info("CMD: %s", " ".join(cmd))
    if dry_run:
        return
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.stdout:
        logging.debug(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr:
            logging.error(result.stderr.strip())
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")


def collect_files(directory: Path, suffixes: tuple[str, ...]) -> list[Path]:
    files = [
        path
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in suffixes
    ]
    return files


def predict_proteins(
    genomes: list[Path],
    protein_dir: Path,
    mode: str,
    force: bool,
    dry_run: bool,
) -> dict[str, Path]:
    protein_dir.mkdir(parents=True, exist_ok=True)
    protein_files: dict[str, Path] = {}

    for genome in genomes:
        sample = genome.stem
        protein = protein_dir / f"{sample}.faa"
        protein_files[sample] = protein

        if nonempty(protein) and not force:
            logging.info("Skip Prodigal; existing protein file found: %s", protein)
            continue

        cmd = [
            "prodigal",
            "-i",
            str(genome),
            "-a",
            str(protein),
            "-p",
            mode,
            "-q",
        ]
        run_command(cmd, dry_run=dry_run)

    return protein_files


def run_hmmsearches(
    hmms: list[Path],
    protein_files: dict[str, Path],
    output_dir: Path,
    threads: int,
    force: bool,
    dry_run: bool,
) -> None:
    for hmm in hmms:
        family = hmm.stem
        family_dir = output_dir / family / "hmmsearch"
        family_dir.mkdir(parents=True, exist_ok=True)

        for sample, protein in protein_files.items():
            if not dry_run and not nonempty(protein):
                logging.warning("Skip %s for %s; protein file is missing or empty.", family, sample)
                continue

            output_tbl = family_dir / f"{sample}.tbl"
            if nonempty(output_tbl) and not force:
                logging.info("Skip hmmsearch; existing tblout found: %s", output_tbl)
                continue

            cmd = [
                "hmmsearch",
                "--cpu",
                str(max(1, threads)),
                "--tblout",
                str(output_tbl),
                "--noali",
                str(hmm),
                str(protein),
            ]
            run_command(cmd, dry_run=dry_run)


def main() -> None:
    args = parse_args()
    genome_dir = args.genome_dir.resolve()
    hmm_dir = args.hmm_dir.resolve()
    protein_dir = (args.protein_dir or genome_dir / "AA").resolve()
    output_dir = args.output_dir.resolve()
    log_file = (args.log_file or output_dir / "run_hmmsearch_batch.log").resolve()
    suffixes = tuple(s.strip().lower() for s in args.genome_suffixes.split(",") if s.strip())

    setup_logging(log_file)
    check_executable("prodigal", dry_run=args.dry_run)
    check_executable("hmmsearch", dry_run=args.dry_run)

    if not genome_dir.is_dir():
        raise SystemExit(f"Genome directory not found: {genome_dir}")
    if not hmm_dir.is_dir():
        raise SystemExit(f"HMM directory not found: {hmm_dir}")

    genomes = collect_files(genome_dir, suffixes)
    hmms = collect_files(hmm_dir, (".hmm",))
    if not genomes:
        raise SystemExit(f"No genome FASTA files found in {genome_dir} with suffixes {suffixes}")
    if not hmms:
        raise SystemExit(f"No .hmm files found in {hmm_dir}")

    logging.info("Found %d genome files and %d HMM profiles.", len(genomes), len(hmms))
    logging.info("Protein directory: %s", protein_dir)
    logging.info("Output directory: %s", output_dir)

    protein_files = predict_proteins(
        genomes=genomes,
        protein_dir=protein_dir,
        mode=args.prodigal_mode,
        force=args.force_prodigal,
        dry_run=args.dry_run,
    )
    run_hmmsearches(
        hmms=hmms,
        protein_files=protein_files,
        output_dir=output_dir,
        threads=args.threads,
        force=args.force_hmmsearch,
        dry_run=args.dry_run,
    )

    logging.info("Completed MAG/WGS BileActome HMM search workflow.")


if __name__ == "__main__":
    main()
