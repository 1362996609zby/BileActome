# BileActome

BileActome is a Linux command-line software package for annotating microbial bile acid metabolism genes in genomes, MAG/WGS assemblies, and non-redundant metagenomic gene catalogs. It packages 27 curated profile-HMM families and provides reproducible genome-level annotation and community-level abundance workflows.

Software name: BileActome Microbial Bile Acid Metabolism Gene Annotation and Abundance Analysis Software.
Copyright holder: China Agricultural University. Application-material version:
V1.0; package version: 1.0.1. This is the CLI distribution; the paper-release
resources are available separately in the original GitHub repository.

## Installation

```bash
mamba env create -f environment.yml --strict-channel-priority
conda activate bileactome
python -m pip install . --no-deps
bileactome doctor
bileactome db verify
```

The official Bioconda package is being prepared and is not yet published.
The intended command after review and acceptance is:

```bash
mamba create -n bileactome --strict-channel-priority -c conda-forge -c bioconda bileactome=1.0.1
```

Runtime dependencies: Python 3.10–3.12, Bash 4+, HMMER 3.4.x, Prodigal 2.6.x
(>=2.6.3), Bowtie2 2.5.x (>=2.5.4), Biopython, NumPy, pandas and openpyxl.
`pip` installs Python dependencies; it does not install HMMER, Prodigal or
Bowtie2. Use Conda to provide those executables. A pinned reference environment
is supplied in `environment.release.yml`; only the versions and Linux platform
listed in the release validation report are claimed verified.
Both the HMMs and toy data ship with the package; routine use requires no
download, email verification, network access or writes to the installed HMMs.

## Main commands

```bash
bileactome --version
bileactome
bileactome --banner --help
bileactome license
bileactome doctor
bileactome db verify
bileactome self-test --workflow all
bileactome mag run --genome-dir genomes --output-dir results/mag --threads 8
bileactome catalog run --protein-fasta proteins.fa --cds-fasta cds.fa --reads-dir clean_reads --output-dir results/catalog --threads 8
bileactome results validate --project-dir results/mag
```

The default full-sequence HMMER threshold is `E <= 1e-3`. A profile-HMM hit is a sequence-level functional annotation and does not by itself prove expression, catalytic activity, substrate specificity, or completion of a pathway.

## Terminal logo

The ASCII logo appears on stderr in interactive terminal sessions. Use
`--banner` to display it in a non-interactive session, or `--no-banner` /
`BILEACTOME_NO_BANNER=1` to suppress it. `--version` remains one line.
JSON output stays on stdout without a logo, so `bileactome db verify > db.json`
can be parsed directly. Calling `bileactome` without arguments shows help
and exits successfully.

## Inputs and outputs

`mag run` takes a directory of nucleotide genome/MAG/WGS FASTA files and
returns per-genome hits, optional candidate proteins and a genome-by-family
count matrix. Counts are not metagenomic abundance estimates.
`catalog run` takes matching non-redundant protein/CDS FASTA files and a
directory of paired clean FASTQ reads, and returns gene/function mappings,
gene RPKM, family summed abundance, relative abundance and sample-wise CLR
matrices. Existing outputs and checkpoints support resume; use a fresh
output directory for changed inputs or parameters. `--force` is an explicit
request to recompute. Logs and run manifests are written to the output
directory, and `results validate` checks output structure and values.

## License and citation

Starting with version 1.0.1, original CLI code, tests, packaging and release
documentation use the OSI-approved [BSD 3-Clause License](LICENSE).
Research and commercial use, modification and redistribution are permitted
under its terms without a separate commercial authorization. Retain license
notices; author or institutional endorsement requires permission.

Project and collaboration contacts: Bing Wang (wangb@cau.edu.cn)
and Boyan Zhang (1362996609zby@gmail.com).

The 27 paper HMMs, legacy scripts and toy data remain [CC BY 4.0](LICENSES/CC-BY-4.0.txt),
which permits commercial reuse under its terms. See [NOTICE](NOTICE) for the
directory-level license map. The CLI license does not revoke those permissions.

Zhang B, Jiang X, Zhao H, Wang B. BileActome reveals community-assembled bile
acid metabolism in the rumen microbiome. ISME Communications. 2026;6(1):ycag205.
https://doi.org/10.1093/ismeco/ycag205

## Troubleshooting and release instructions

Run `bileactome doctor` to identify missing executable paths and package
versions. Run `bileactome db verify` to verify all 27 HMM checksums.
Self-test fixtures are installed with the wheel and can run outside the
source tree. For interrupted analyses, retain the output directory and logs
and rerun the same command. Do not reuse completed output directories after
changing inputs or thresholds. See [docs/RELEASE.md](docs/RELEASE.md) for local
Conda builds, release archive hashes, license notices and Bioconda PR
preparation.
