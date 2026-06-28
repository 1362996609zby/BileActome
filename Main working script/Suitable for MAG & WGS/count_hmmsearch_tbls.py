#!/usr/bin/env python3
"""Build a genome-by-family hit count matrix from HMMER tblout files."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count HMMER tblout hits passing a full-sequence E-value cutoff."
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=Path("."),
        help="Directory containing <family>/hmmsearch/*.tbl outputs. Default: current directory.",
    )
    parser.add_argument(
        "--evalue",
        type=float,
        default=1e-3,
        help="Full-sequence E-value threshold. Default: 1e-3.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output TSV matrix. Default: <result-dir>/hmmsearch_counts_E1e-03.tsv.",
    )
    return parser.parse_args()


def count_tbl_hits(tbl_file: Path, evalue_threshold: float) -> int:
    hit_count = 0
    with tbl_file.open() as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.strip().split()
            if len(fields) < 5:
                continue
            try:
                full_evalue = float(fields[4])
            except ValueError:
                continue
            if full_evalue <= evalue_threshold:
                hit_count += 1
    return hit_count


def main() -> None:
    args = parse_args()
    result_dir = args.result_dir.resolve()
    output = args.output or result_dir / f"hmmsearch_counts_E{args.evalue:.0e}.tsv"

    if not result_dir.is_dir():
        raise SystemExit(f"Result directory not found: {result_dir}")

    tbl_files = sorted(result_dir.glob("*/hmmsearch/*.tbl"))
    if not tbl_files:
        raise SystemExit(f"No .tbl files found under {result_dir}/*/hmmsearch/")

    matrix: dict[str, dict[str, int]] = defaultdict(dict)
    families: set[str] = set()
    genomes: set[str] = set()

    for tbl_file in tbl_files:
        family = tbl_file.parent.parent.name
        genome = tbl_file.stem
        families.add(family)
        genomes.add(genome)
        matrix[genome][family] = matrix[genome].get(family, 0) + count_tbl_hits(
            tbl_file, args.evalue
        )

    ordered_families = sorted(families)
    ordered_genomes = sorted(genomes)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["Genome"] + ordered_families)
        for genome in ordered_genomes:
            writer.writerow([genome] + [matrix[genome].get(family, 0) for family in ordered_families])

    print(f"Counted {len(tbl_files)} tblout files.")
    print(f"Genomes: {len(ordered_genomes)}")
    print(f"Families: {len(ordered_families)}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
