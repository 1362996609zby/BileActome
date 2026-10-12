from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .banner import license_summary, render_banner
from .database import verify_database, write_database_manifest
from .doctor import diagnose, print_diagnosis, write_report
from .paths import default_database_dir


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be > 0")
    return parsed


def add_database_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database-dir", type=Path, default=None, help=f"BileActome HMM directory (default: {default_database_dir()})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bileactome", description="BileActome microbial bile acid metabolism annotation and abundance analysis")
    parser.add_argument("--version", action="version", version=f"BileActome {__version__}")
    banner_group = parser.add_mutually_exclusive_group()
    banner_group.add_argument("--banner", action="store_true", help="Show ASCII logo on stderr, including in redirected sessions")
    banner_group.add_argument("--no-banner", action="store_true", help="Suppress the terminal logo")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("license", help="Show software ownership and component license summary")

    doctor_parser = sub.add_parser("doctor", help="Diagnose software, tool, Python-package, and database availability")
    doctor_parser.add_argument("--workflow", choices=["all", "mag", "catalog"], default="all")
    doctor_parser.add_argument("--json", type=Path, default=None, help="Write a machine-readable report")
    add_database_argument(doctor_parser)

    db_parser = sub.add_parser("db", help="Manage and verify the BileActome HMM database")
    db_sub = db_parser.add_subparsers(dest="db_command", required=True)
    db_verify = db_sub.add_parser("verify", help="Verify 27 HMM files using the database manifest")
    db_verify.add_argument("--json", type=Path, default=None)
    add_database_argument(db_verify)
    db_manifest = db_sub.add_parser("build-manifest", help="Build a database manifest for a release")
    db_manifest.add_argument("--output", type=Path, default=None)
    add_database_argument(db_manifest)

    mag_parser = sub.add_parser("mag", help="Genome, WGS, and MAG annotation workflow")
    mag_sub = mag_parser.add_subparsers(dest="mag_command", required=True)
    mag_run = mag_sub.add_parser("run", help="Run protein prediction, HMM searches, hit extraction, and count summary")
    mag_run.add_argument("--genome-dir", type=Path, required=True)
    mag_run.add_argument("--output-dir", type=Path, required=True)
    mag_run.add_argument("--threads", type=positive_int, default=1)
    mag_run.add_argument("--evalue", type=positive_float, default=1e-3)
    mag_run.add_argument("--prodigal-mode", choices=["meta", "single"], default="meta")
    mag_run.add_argument("--no-extract-hits", action="store_true")
    mag_run.add_argument("--force", action="store_true")
    mag_run.add_argument("--verbose", action="store_true")
    add_database_argument(mag_run)

    catalog_parser = sub.add_parser("catalog", help="Non-redundant metagenomic gene-catalog workflow")
    catalog_sub = catalog_parser.add_subparsers(dest="catalog_command", required=True)
    catalog_run = catalog_sub.add_parser("run", help="Run HMM annotation, CDS extraction, mapping, RPKM, and family matrices")
    catalog_run.add_argument("--protein-fasta", type=Path, required=True)
    catalog_run.add_argument("--cds-fasta", type=Path, required=True)
    catalog_run.add_argument("--reads-dir", type=Path, required=True)
    catalog_run.add_argument("--output-dir", type=Path, required=True)
    catalog_run.add_argument("--threads", type=positive_int, default=8)
    catalog_run.add_argument("--evalue", type=positive_float, default=1e-3)
    catalog_run.add_argument("--dom-evalue", type=positive_float, default=1e-3)
    catalog_run.add_argument("--epsilon", type=positive_float, default=1e-12)
    catalog_run.add_argument("--id-regex", default=None)
    catalog_run.add_argument("--force", action="store_true")
    catalog_run.add_argument("--verbose", action="store_true")
    add_database_argument(catalog_run)

    selftest_parser = sub.add_parser("self-test", help="Run an end-to-end installation test using bundled toy data")
    selftest_parser.add_argument("--workflow", choices=["mag", "catalog", "all"], default="all")
    selftest_parser.add_argument("--fixture-dir", type=Path, default=None)
    selftest_parser.add_argument("--output-dir", type=Path, default=None)
    selftest_parser.add_argument("--threads", type=positive_int, default=2)

    results_parser = sub.add_parser("results", help="Validate BileActome project outputs")
    results_sub = results_parser.add_subparsers(dest="results_command", required=True)
    results_validate = results_sub.add_parser("validate", help="Validate files, columns, matrices, and numeric constraints")
    results_validate.add_argument("--project-dir", type=Path, required=True)
    return parser


def dispatch(args: argparse.Namespace) -> int:
    if args.command == "license":
        print(license_summary())
        return 0
    if args.command == "doctor":
        report = diagnose(args.database_dir, args.workflow)
        print_diagnosis(report)
        if args.json:
            write_report(report, args.json)
        return 0 if report["ok"] else 2
    if args.command == "db" and args.db_command == "verify":
        report = verify_database(args.database_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.json:
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if report["ok"] else 2
    if args.command == "db" and args.db_command == "build-manifest":
        print(write_database_manifest(args.database_dir, args.output))
        return 0
    if args.command == "mag" and args.mag_command == "run":
        from .mag import run_mag

        print(run_mag(args.genome_dir, args.output_dir, args.database_dir, args.threads, args.evalue, args.prodigal_mode, not args.no_extract_hits, args.force, args.verbose))
        return 0
    if args.command == "catalog" and args.catalog_command == "run":
        from .catalog import run_catalog

        print(run_catalog(args.protein_fasta, args.cds_fasta, args.reads_dir, args.output_dir, args.database_dir, args.threads, args.evalue, args.dom_evalue, args.epsilon, args.id_regex, args.force, args.verbose))
        return 0
    if args.command == "self-test":
        from .selftest import run_selftest

        report = run_selftest(args.workflow, args.fixture_dir, args.output_dir, args.threads)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2
    if args.command == "results" and args.results_command == "validate":
        from .validation import validate_project

        report = validate_project(args.project_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2
    raise RuntimeError("Unhandled command")


def main(argv: list[str] | None = None) -> None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    # Global banner switches may be used before or after a subcommand.
    force_banner = "--banner" in arguments
    suppress_banner = "--no-banner" in arguments or (not force_banner and os.environ.get("BILEACTOME_NO_BANNER") == "1")
    if force_banner and "--no-banner" in arguments:
        build_parser().error("--banner and --no-banner cannot be used together")
    arguments = [item for item in arguments if item not in {"--banner", "--no-banner"}]
    if not suppress_banner and (force_banner or (sys.stderr.isatty() and "--version" not in arguments)):
        print(render_banner(), file=sys.stderr)
    parser = build_parser()
    if not arguments:
        parser.print_help()
        raise SystemExit(0)
    try:
        status = dispatch(parser.parse_args(arguments))
    except KeyboardInterrupt:
        print("Interrupted by user; existing outputs and logs were retained.", file=sys.stderr)
        status = 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        status = 1
    raise SystemExit(status)
