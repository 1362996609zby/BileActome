# BileActome MAG/WGS Annotation Workflow

This workflow annotates bile-acid-metabolism genes in microbial genomes,
isolate whole-genome sequences (WGS), or metagenome-assembled genomes (MAGs)
using the BileActome profile HMM database.

The current workflow is designed to run all BileActome HMM families in one
command. Prodigal is run once per genome to generate predicted proteins, and
the same protein files are then reused for every HMM search.

## 1. What This Workflow Does

For each genome or MAG, the workflow:

1. predicts protein sequences from nucleotide FASTA files using Prodigal;
2. searches the predicted proteins against all `.hmm` files in a BileActome HMM
   directory using HMMER `hmmsearch`;
3. writes one HMMER `tblout` file per genome and per BileActome family;
4. optionally extracts matched protein sequences passing the E-value threshold;
5. summarizes family-level hit counts across genomes.

This workflow is for genome-level annotation. It produces genome-by-family hit
counts, not metagenomic abundance estimates. For read-based abundance profiling,
use the non-redundant gene catalog workflow.

## 2. Required Inputs

### 2.1 BileActome HMM Profiles

Download all 27 BileActome `.hmm` files from:

```text
https://github.com/1362996609zby/Bile_acid_v2/tree/main/database%20file
```

Place them in one directory, for example:

```text
project_root/BileActome_HMMs/
├── 12ahsdh_final.hmm
├── 12bhsdh_final.hmm
├── 3ahsdh_nadh_final.hmm
├── ...
├── BaiP_final.hmm
├── BSH_g_final.hmm
└── BSH_t_final.hmm
```

The HMM basename is used as the family identifier. For example,
`BaiE_final.hmm` is reported as `BaiE_final`.

### 2.2 Genome or MAG FASTA Files

Prepare nucleotide FASTA files in one directory:

```text
genomes/
├── genome_001.fna
├── genome_002.fna
└── genome_003.fna
```

Supported suffixes are `.fna`, `.fa`, and `.fasta` by default. Each file should
represent one genome, WGS assembly, or MAG. The file stem is used as the genome
ID in output files.

## 3. Software Environment

Create and activate a conda environment:

```bash
conda create -n bileactome_hmm -c conda-forge -c bioconda \
  python=3.10 hmmer prodigal
conda activate bileactome_hmm
```

Check that the required tools are available:

```bash
prodigal -h
hmmsearch -h
python --version
```

## 4. Recommended Directory Layout

```text
project_root/
├── BileActome_HMMs/
│   ├── BaiE_final.hmm
│   ├── BaiCD_final.hmm
│   └── ...
├── genomes/
│   ├── genome_001.fna
│   ├── genome_002.fna
│   └── genome_003.fna
├── run_hmmsearch_batch.py
├── extract_hits_from_fasta.py
└── count_hmmsearch_tbls.py
```

## 5. Step 1: Predict Proteins and Run All HMM Searches

Run:

```bash
python run_hmmsearch_batch.py \
  --genome-dir genomes \
  --hmm-dir BileActome_HMMs \
  --protein-dir genomes/AA \
  --output-dir bileactome_mag_wgs_results \
  --threads 8
```

Main parameters:

| Parameter | Meaning |
|---|---|
| `--genome-dir` | Directory containing MAG/WGS nucleotide FASTA files |
| `--hmm-dir` | Directory containing all BileActome `.hmm` files |
| `--protein-dir` | Directory for Prodigal-predicted `.faa` files |
| `--output-dir` | Directory for family-specific HMMER outputs |
| `--threads` | CPU threads passed to `hmmsearch --cpu` |
| `--prodigal-mode` | Prodigal mode, `meta` by default |
| `--force-prodigal` | Regenerate `.faa` files even if they already exist |
| `--force-hmmsearch` | Regenerate `.tbl` files even if they already exist |
| `--dry-run` | Print planned commands without executing them |

The script is resumable. Existing non-empty `.faa` and `.tbl` files are skipped
unless `--force-prodigal` or `--force-hmmsearch` is supplied.

Expected outputs:

```text
genomes/AA/
├── genome_001.faa
├── genome_002.faa
└── genome_003.faa

bileactome_mag_wgs_results/
├── BaiE_final/
│   └── hmmsearch/
│       ├── genome_001.tbl
│       ├── genome_002.tbl
│       └── genome_003.tbl
├── BaiCD_final/
│   └── hmmsearch/
│       ├── genome_001.tbl
│       ├── genome_002.tbl
│       └── genome_003.tbl
└── run_hmmsearch_batch.log
```

## 6. Step 2: Extract Matched Protein Sequences

After HMMER searches finish, extract protein sequences passing the full-sequence
E-value threshold:

```bash
python extract_hits_from_fasta.py \
  --result-dir bileactome_mag_wgs_results \
  --protein-dir genomes/AA \
  --evalue 1e-3
```

Expected outputs:

```text
bileactome_mag_wgs_results/
├── BaiE_final/
│   └── hmmsearch/
│       └── hits/
│           ├── genome_001_hits.fasta
│           └── genome_002_hits.fasta
└── extract_hits_from_fasta.log
```

## 7. Step 3: Count HMM Hits Across Genomes and Families

The helper script `count_hmmsearch_tbls.py` summarizes all `.tbl` files into a
genome-by-family hit count matrix:

```bash
python count_hmmsearch_tbls.py \
  --result-dir bileactome_mag_wgs_results \
  --evalue 1e-3
```

Expected output:

```text
bileactome_mag_wgs_results/hmmsearch_counts_E1e-03.tsv
```

Rows are genome/MAG IDs. Columns are BileActome families. Values are the number
of hits with full-sequence E-value <= `1e-3`.

## 8. Output Interpretation

The MAG/WGS workflow supports:

- presence/absence analysis of BileActome families in genomes;
- family-level detection rate across MAG/WGS datasets;
- Bai module completeness analysis;
- genome-level guild classification;
- comparison between BileActome and KEGG-based annotations;
- extraction of candidate sequences for alignment or phylogenetic analysis.

For genome-level pathway interpretation, a binary matrix is often useful:

```text
presence = 1 if hit_count > 0 else 0
```

## 9. Notes and Limitations

1. This workflow uses `hmmsearch` directly on individual HMM files, so `hmmpress`
   is not required.
2. The default HMMER hit threshold used by the downstream parser is
   full-sequence E-value <= `1e-3`.
3. Hit count is not abundance. For metagenomic abundance, use the
   non-redundant gene catalog workflow with Bowtie2 mapping and RPKM/relative
   abundance/CLR transformation.
4. MAG fragmentation can split true gene neighborhoods across contigs, so
   neighborhood or operon-level interpretation should be made cautiously.
5. Existing output files are skipped by default to support checkpoint/resume
   behavior in large datasets.

## 10. Minimal Command Example

```bash
conda activate bileactome_hmm

python run_hmmsearch_batch.py \
  --genome-dir genomes \
  --hmm-dir BileActome_HMMs \
  --protein-dir genomes/AA \
  --output-dir bileactome_mag_wgs_results \
  --threads 8

python extract_hits_from_fasta.py \
  --result-dir bileactome_mag_wgs_results \
  --protein-dir genomes/AA \
  --evalue 1e-3

cd bileactome_mag_wgs_results
cd ..
python count_hmmsearch_tbls.py \
  --result-dir bileactome_mag_wgs_results \
  --evalue 1e-3
```
