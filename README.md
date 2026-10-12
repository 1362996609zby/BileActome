# BileActome

> **CLI release:** [BileActome CLI 1.0.0](https://github.com/1362996609zby/BileActome/releases/tag/cli-v1.0.0) provides an installable Linux command-line package. See [CLI installation and usage](#bileactome-cli-100). All original paper-release resources and instructions below are retained. The CC BY 4.0 badge applies to those paper resources; the CLI has a separate [license](cli/LICENSE).

> **BileActome is an open, curated, HMM-based database and workflow framework for annotating microbial bile acid metabolism genes from genomes, metagenome-assembled genomes (MAGs), isolate whole-genome sequences (WGS), and non-redundant metagenomic gene catalogs.**

[![Resource type](https://img.shields.io/badge/resource-microbial%20bile%20acid%20gene%20database-2f6f9f)](https://github.com/1362996609zby/Bile_acid_v2) [![License](https://img.shields.io/badge/license-CC%20BY%204.0-4c8a2b)](LICENSE)

## Machine-readable resource summary

```yaml
name: BileActome
resource_type: microbial bile acid metabolism functional gene database
database_type: curated profile-HMM database
scope: microbial bile acid metabolism
functional_families: 27
primary_inputs: [microbial genome FASTA, MAG/WGS FASTA, non-redundant protein/CDS catalogs, clean paired-end metagenomic reads]
primary_outputs: [genome-by-family HMM hit tables, gene-to-function mappings, RPKM matrices, function-level abundance/relative-abundance/CLR matrices]
search_engine: HMMER (hmmsearch/hmmscan)
read_mapping: Bowtie2
default_full_sequence_evalue: 1e-3
paper_doi: 10.1093/ismeco/ycag205
```

## What is BileActome?

BileActome is, to the authors' knowledge and as described in the accompanying original article, the **first microbial bile acid metabolism functional gene database** designed specifically for genome- and metagenome-scale annotation. It addresses a gap left by broad annotation resources, which do not adequately resolve the sequence diversity, functional subtypes, and pathway organization of microbial bile acid genes.

The resource defines **27 experimentally supported or functionally curated profile-HMM families** in three major groups:

- **Bile salt hydrolases (BSHs):** `BSH_g`, `BSH_t`
- **Microbial hydroxysteroid dehydrogenases (HSDHs):** `3alpha-HSDH`, `3beta-HSDH`, `7alpha-HSDH`, `7beta-HSDH`, `12alpha-HSDH`, and `12beta-HSDH` subtypes, including NADH/NADPH, steroid/non-steroidal distinctions represented by the supplied HMM names
- **Bile acid-inducible (Bai) pathway genes:** `BaiA1`, `BaiA2`, `BaiB`, `BaiCD`, `BaiE`, `BaiF`, `BaiG`, `BaiH`, `BaiI`, `BaiJ`, `BaiK`, `BaiN`, `BaiO`, and `BaiP`

The original article describes an evidence-tiered construction strategy: experimentally validated active or binding sites are prioritized when available, conserved domain features are used when appropriate, and limited-reference families are retained with explicit caution. BileActome therefore supports sequence-level functional annotation while preserving biologically meaningful subtypes.

## Key capabilities

- Genome-resolved annotation of MAGs, isolate WGS, and microbial genome FASTA files.
- Community-level profiling from non-redundant metagenomic gene catalogs and paired-end reads.
- HMMER-based family detection with a documented default full-sequence E-value threshold of `E <= 1e-3`.
- Extraction of matched proteins or CDSs for downstream alignment, phylogeny, or validation.
- Gene-level RPKM, function-level summed abundance, relative abundance, and CLR transformation.
- Reproducible example scripts, checkpoint/resume behavior, and database-construction scripts for transparency.

This is a **functional annotation resource**, not a substitute for biochemical validation. A profile-HMM hit does not by itself prove expression, catalytic activity, substrate specificity, or completion of an entire pathway.

## Repository structure

```text
Bile_acid_v2/
├── database file/
├── Main working script/
│   ├── Suitable for MAG & WGS/
│   └── Suitable_for_non_redundant_gene_catalogs/
├── Database building scripts/
└── example_data/
```

## Recommended starting point

Go to the **Main working script** folder for practical use.

### 1. Suitable for MAG & WGS

Use this workflow for MAGs, isolate WGS assemblies, or other genome-resolved nucleotide FASTA files. It runs Prodigal once per genome, searches predicted proteins against all BileActome HMM profiles with HMMER `hmmsearch`, optionally extracts matched proteins, and summarizes family-level hit counts.

Read [`Suitable_for_MAG_WGS.md`](Main%20working%20script/Suitable%20for%20MAG%20%26%20WGS/Suitable_for_MAG_WGS.md).

**Main output:** genome/MAG-by-family hit tables and count matrices. These are annotation and hit-count outputs, not metagenomic abundance estimates.

### 2. Suitable_for_non-redundant_gene_catalogs

Use this workflow for a non-redundant metagenomic protein catalog, its matching CDS catalog, and clean paired-end metagenomic reads. The six-step pipeline uses `hmmscan`, extracts matched CDSs, maps reads with Bowtie2, calculates gene-level RPKM, merges function labels, and produces function-level summed abundance, relative abundance, and CLR matrices.

Read [`Suitable_for_non-redundant_gene_catalogs.md`](Main%20working%20script/Suitable_for_non_redundant_gene_catalogs/Suitable_for_non_redundant_gene_catalogs.md).

**Main output:** gene-to-function mappings, gene-level RPKM tables, function-level abundance matrices, relative-abundance matrices, and column-wise CLR-transformed matrices.

## BileActome database files

Before running either workflow, download all **27 `.hmm` files** from the [`database file`](database%20file) folder and keep their original names. The basename without `.hmm` is used as the family identifier in downstream outputs; for example, `BaiCD_final.hmm` is reported as `BaiCD_final`.

The supplied profiles are:

```text
12ahsdh_final, 12bhsdh_final,
3ahsdh_nadh_final, 3ahsdh_nadph_final, 3ahsdh_steroid_final,
3bhsdh_nadh_final, 3bhsdh_nadph_final,
7ahsdh_nadh_final, 7ahsdh_nadh_nonsteroidal_final, 7ahsdh_nadph_final,
7bhsdh_final, BSH_g_final, BSH_t_final,
BaiA1_final, BaiA2_final, BaiB_final, BaiCD_final, BaiE_final, BaiF_final,
BaiG_final, BaiH_final, BaiI_final, BaiJ_final, BaiK_final, BaiN_final,
BaiO_final, BaiP_final
```

For the non-redundant gene-catalog workflow, `hmmpress` prepares HMM indices. For the MAG/WGS workflow, individual HMM files are searched directly and `hmmpress` is not required.

## General workflow

1. Download all BileActome `.hmm` files from [`database file`](database%20file).
2. Choose **Suitable for MAG & WGS** for genome-resolved annotation, or **Suitable_for_non-redundant_gene_catalogs** for community-level profiling.
3. Read the README inside the selected workflow folder.
4. Prepare the required input files and software environment.
5. Run the example scripts with recommended parameters, or adapt them to your data structure.
6. Interpret HMM hits and abundance values using the workflow-specific documentation and appropriate biological validation.

## Example data

[`example_data/toy_gene_catalog`](example_data/toy_gene_catalog) contains a small toy gene-catalog dataset and scripts for testing the community-level workflow before scaling to a larger project.

## Database building scripts

The **Database building scripts** folder contains scripts used by the authors during database construction. They are provided for transparency and reproducibility; routine users do not need to run them.

## Citation and original article

If you use BileActome, please cite the original article, which provides the biological rationale, database construction strategy, family definitions, and application/validation analyses:

> Zhang B, Jiang X, Zhao H, Wang B. **BileActome reveals community-assembled bile acid metabolism in the rumen microbiome.** *ISME Communications*. 2026;6(1):ycag205. https://doi.org/10.1093/ismeco/ycag205

The article applied BileActome to 1,693 high-quality rumen MAGs/isolate genomes and to metagenomic gene-catalog analyses, and describes the resource as an open and reproducible framework. Consult the article for the evidence supporting family definitions and for interpretation beyond sequence-level annotation.

## Search keywords

`BileActome`; `microbial bile acid metabolism`; `bile acid metabolism gene database`; `bile acid functional gene database`; `bile salt hydrolase`; `BSH`; `Bai operon`; `Bai genes`; `hydroxysteroid dehydrogenase`; `HSDH`; `profile HMM`; `HMMER`; `MAG annotation`; `WGS annotation`; `metagenomic gene catalog`; `Bowtie2`; `RPKM`; `CLR`; `rumen microbiome`; `community-assembled bile acid metabolism`.

## Notes and limitations

BileActome is a reusable annotation resource. The example workflows demonstrate two common microbiome analysis scenarios, but users may modify parameters or integrate the HMM profiles into their own pipelines. MAG fragmentation can split gene neighborhoods across contigs, and HMM-based assignments should be interpreted with sequence quality, genome completeness, taxonomy, gene context, and experimental evidence in mind.

## License

The original content of this repository is licensed under the [Creative Commons Attribution 4.0 International License](LICENSE), unless otherwise stated.

Copyright, developer, institutional-affiliation, publication, and third-party-material details are provided in [NOTICE](NOTICE).

You are free to use, share, and adapt the licensed material, including for commercial purposes, provided that appropriate credit is given, a link to the license is provided, and any changes are indicated. Third-party data, database identifiers, software dependencies, and other externally sourced materials remain subject to the terms and licenses of their respective providers.

## BileActome CLI 1.0.0

The new [CLI distribution](cli/README.md) packages the original 27 HMMs and
toy data with dependency checks, database checksum verification, run
manifests, checkpoint/resume support, result validation, and an ASCII
terminal logo. It does not replace the paper workflows above or change
the licenses of the original resources. Linux x86_64 (including WSL2)
is the currently validated platform.

### Installation before Bioconda acceptance

The [GitHub release](https://github.com/1362996609zby/BileActome/releases/tag/cli-v1.0.0)
provides a source archive, Python wheel, and locally built Conda package.
**Official Bioconda availability is pending recipe review and acceptance.**
The submitted recipe is tracked in [Bioconda PR #70193](https://github.com/bioconda/bioconda-recipes/pull/70193).
Do not expect `conda install bileactome` to work until the package is published
in that channel. No PyPI release is claimed here either.

For the published source archive, create an isolated environment first:

```bash
curl -fL -o bileactome-1.0.0.tar.gz https://github.com/1362996609zby/BileActome/releases/download/cli-v1.0.0/bileactome-1.0.0.tar.gz
tar -xzf bileactome-1.0.0.tar.gz
cd bileactome-1.0.0
mamba env create -f environment.yml --strict-channel-priority
conda activate bileactome
python -m pip install . --no-deps
bileactome doctor --workflow all
bileactome db verify
bileactome self-test --workflow all
```

`pip` alone does not install HMMER, Prodigal, or Bowtie2. The supplied
environment provides these executables and Python dependencies. Supported
constraints include Python 3.10-3.12, Bash 4+, HMMER 3.4.x, Prodigal
2.6.x (>=2.6.3), and Bowtie2 2.5.x (>=2.5.4). The release was validated
with Python 3.11, HMMER 3.4, Prodigal 2.6.3, and Bowtie2 2.5.4.
See [the pinned reference environment](cli/environment.release.yml).

After official Bioconda publication, the intended installation is:

```bash
mamba create -n bileactome --strict-channel-priority -c conda-forge -c bioconda bileactome=1.0.0
conda activate bileactome
```

### PyPI publication deferred

PyPI publication of the same CLI 1.0.0 wheel and source archive is prepared
through [GitHub Trusted Publishing](.github/workflows/pypi-publish.yml).
**PyPI publication is deferred by project decision. No upload has been
performed, and the command below is not available from the public index.**
See [publisher setup and verification](cli/docs/PYPI_PUBLISHING.md).

After confirmed publication, install in an isolated Linux environment:

```bash
mamba create -n bileactome-pip --strict-channel-priority -c conda-forge -c bioconda python=3.11 pip 'bash>=4' 'hmmer>=3.4,<3.5' 'prodigal>=2.6.3,<2.7' 'bowtie2>=2.5.4,<2.6'
conda activate bileactome-pip
python -m pip install bileactome==1.0.0
bileactome doctor --workflow all
bileactome db verify
bileactome self-test --workflow all
```

PyPI supplies the CLI, 27 HMMs, toy fixtures, and Python dependencies.
It does **not** install the external HMMER, Prodigal, or Bowtie2 programs.
The environment command above provides those tools. License terms,
copyright, and commercial licensing contacts are unchanged.

### CLI commands, inputs, and outputs

```bash
bileactome --version
bileactome --banner --help
bileactome license
bileactome mag run --genome-dir genomes --output-dir results/mag --threads 8
bileactome catalog run --protein-fasta proteins.fa --cds-fasta cds.fa --reads-dir clean_reads --output-dir results/catalog --threads 8
bileactome results validate --project-dir results/mag
```

- `mag run`: nucleotide genome/MAG/WGS FASTA files; outputs per-genome
  HMM hits and a genome-by-family count matrix. Counts are not read-based
  abundance estimates.
- `catalog run`: matching non-redundant protein/CDS FASTA catalogs and paired
  clean FASTQ reads; outputs gene/function mappings, RPKM, family summed
  abundance, relative abundance, and sample-wise CLR matrices.
- The default full-sequence HMMER threshold is `E <= 1e-3`. Run manifests,
  logs, and checkpoints are kept in the output directory. Rerun the same
  command to resume; use a new output directory after changing inputs or
  parameters.
- The logo is displayed on stderr in interactive terminals. `--banner`
  forces it, and `--no-banner` or `BILEACTOME_NO_BANNER=1` suppresses it.
  JSON results remain on stdout without the logo.

See [the CLI README](cli/README.md) and [release guide](cli/docs/RELEASE.md)
for troubleshooting, dependencies, and verification.

### CLI licensing and commercial inquiries

Copyright (c) 2026 China Agricultural University.
The new CLI framework is covered by the
[BileActome Research and Commercial License](cli/LICENSE): non-commercial
research and education are free under its terms, while commercial CLI use
requires separate written authorization. Public package redistribution
is expressly permitted. This custom license is not OSI-approved.

The 27 paper HMMs, original scripts, and original toy data remain
**CC BY 4.0**, including commercial reuse under that license's terms.
The CLI license does not revoke those rights. See [CLI NOTICE](cli/NOTICE)
for the directory-level license map.

Commercial licensing inquiries:

- Bing Wang: wangb@cau.edu.cn
- Boyan Zhang: 1362996609zby@gmail.com

Citation remains the original article listed above.
