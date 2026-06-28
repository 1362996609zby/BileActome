# Toy Example Dataset for the BileActome Gene-Catalog Workflow

This folder contains a deliberately small toy dataset for checking whether
the non-redundant gene-catalog workflow can run from HMM annotation to
function-level abundance tables.

The dataset is for software testing only. It should not be used for
biological interpretation, benchmarking, or method validation.

## Contents

```text
toy_gene_catalog/
├── gene_catalog/
│   ├── toy_unigenes.protein.fa
│   └── toy_unigenes.CDS.fa
├── clean_reads/
│   ├── toy_sample_A_R1.fastq.gz
│   ├── toy_sample_A_R2.fastq.gz
│   ├── toy_sample_B_R1.fastq.gz
│   └── toy_sample_B_R2.fastq.gz
├── scripts/
│   └── step1-step6 workflow scripts
├── run_toy_example.sh
└── README.md
```

The toy gene catalog contains three synthetic BileActome-like genes
generated from selected HMM consensus sequences and two background genes.
The paired-end reads were simulated from the toy CDS records.

## Requirements

Activate an environment containing the required command-line tools and
Python packages. If the Python packages are in a different environment,
set `PYTHON_BIN` before running the script.

- HMMER (`hmmscan`, `hmmpress`)
- Bowtie2 (`bowtie2`, `bowtie2-build`)
- Python 3 with `biopython`, `pandas`, `numpy`, and `openpyxl`

## Run

From the repository root:

```bash
cd example_data/toy_gene_catalog
bash run_toy_example.sh
```

Example with an explicit Python executable:

```bash
PYTHON_BIN=/path/to/env/bin/python bash run_toy_example.sh
```

## Expected Outputs

Results are written to:

```text
example_data/toy_gene_catalog/toy_results/
```

Key files include:

```text
toy_results/gene_to_function.tsv
toy_results/target_cds.fa
toy_results/abundance/*_rpkm.tsv
toy_results/results/abundance_merged_with_function.tsv
toy_results/results/FunctionSum_matrix.tsv
toy_results/results/Relative_abundance_matrix.tsv
toy_results/results/CLR_matrix.tsv
```

Because this is a tiny synthetic dataset, the purpose is only to confirm
that the scripts, dependencies, paths, and output formats work as expected.
