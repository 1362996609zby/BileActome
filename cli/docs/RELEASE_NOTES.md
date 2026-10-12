# BileActome CLI 1.0.0

Linux command-line workflows for microbial bile acid metabolism gene
annotation in genomes, MAGs/WGS assemblies and metagenomic gene catalogs.

- Includes 27 curated profile-HMM families and bundled toy data.
- Provides MAG annotation and gene-catalog RPKM, family abundance, relative
  abundance and sample-wise CLR workflows.
- Includes dependency diagnosis, database checksum verification, run manifests,
  checkpoint/resume support and result validation.
- Displays an ASCII logo in interactive terminals; progress and banner use
  stderr so JSON stdout remains machine-readable.
- Ships a Python wheel, source distribution and Conda package.

Copyright (c) 2026 China Agricultural University.
CLI: BileActome Research and Commercial License.
Paper HMMs, legacy scripts and toy data: CC BY 4.0.
Non-commercial research and education are free under the CLI license;
commercial CLI use requires separate written authorization.

Commercial licensing inquiries:
- Bing Wang: wangb@cau.edu.cn
- Boyan Zhang: 1362996609zby@gmail.com

Citation: Zhang B, Jiang X, Zhao H, Wang B. BileActome reveals
community-assembled bile acid metabolism in the rumen microbiome.
ISME Communications. 2026;6(1):ycag205.
https://doi.org/10.1093/ismeco/ycag205

Validated on WSL2/Linux x86_64 with Python 3.11, HMMER 3.4, Prodigal 2.6.3
and Bowtie2 2.5.4. Official Bioconda availability requires recipe acceptance.
