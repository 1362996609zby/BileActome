# BileActome CLI 1.0.1

This patch release adopts the OSI-approved BSD-3-Clause license for original
CLI code, tests, packaging and release documentation. Research and commercial
use are permitted without a separate commercial license. The 27 paper HMMs,
legacy scripts, database metadata and toy data remain CC BY 4.0. The combined
distribution declares `BSD-3-Clause AND CC-BY-4.0` for those components.
Copyright remains with China Agricultural University. Retain notices and do
not imply endorsement by the institution or contributors.

No annotation algorithms, HMM profiles, thresholds or abundance formulas are
changed. CLI banner/license messages and version metadata are updated.
The Bioconda source URL uses the version template requested in review.
Earlier 1.0.0 release assets are preserved unchanged. PyPI publication remains
deferred; this release is not uploaded to PyPI.

Linux command-line workflows for microbial bile acid metabolism gene
annotation in genomes, MAGs/WGS assemblies and metagenomic gene catalogs.

- Includes 27 curated profile-HMM families and bundled toy data.
- Provides MAG annotation and gene-catalog RPKM, family abundance, relative
  abundance and sample-wise CLR workflows.
- Includes dependency diagnosis, database checksum verification, run manifests,
  checkpoint/resume support and result validation.
- Displays an ASCII logo in interactive terminals; progress and banner use
  stderr so JSON stdout remains machine-readable.
- Ships a Python wheel and source distribution for Bioconda recipe builds.

Copyright (c) 2026 China Agricultural University.
CLI: BSD-3-Clause.
Paper HMMs, legacy scripts and toy data: CC BY 4.0.
Both licenses permit commercial reuse under their respective terms.

Project and collaboration contacts:
- Bing Wang: wangb@cau.edu.cn
- Boyan Zhang: 1362996609zby@gmail.com

Citation: Zhang B, Jiang X, Zhao H, Wang B. BileActome reveals
community-assembled bile acid metabolism in the rumen microbiome.
ISME Communications. 2026;6(1):ycag205.
https://doi.org/10.1093/ismeco/ycag205

Validated on WSL2/Linux x86_64 with Python 3.11, HMMER 3.4, Prodigal 2.6.3
and Bowtie2 2.5.4. Official Bioconda availability requires recipe acceptance.
