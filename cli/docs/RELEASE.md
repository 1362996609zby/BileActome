# BileActome CLI V1.0 / package 1.0.1 release preparation

Copyright holder: China Agricultural University.
Software name: BileActome Microbial Bile Acid Metabolism Gene Annotation and Abundance Analysis Software.
The reference is the confirmed application-information TXT/Markdown supplied
by the user, with development completion date 2026-09-01. No registration
number or certificate was present in the supplied directory as of 2026-10-12.
The packaging and banner changes are release maintenance; the application
materials and their source-code evidence remain archived unchanged.

## License

CLI code from version 1.0.1: `BSD-3-Clause` in LICENSE.
Paper HMMs, legacy scripts, and toy data: CC BY 4.0 as mapped in NOTICE.
BSD-3-Clause is OSI-approved and permits research and commercial use,
modification and redistribution under its terms. No separate commercial
authorization is required. The combined distribution declares
`BSD-3-Clause AND CC-BY-4.0` for the respective components. Retain notices
and do not imply institutional or contributor endorsement.

The BSD license does not restrict independent commercial use of the
paper-release HMMs and scripts. CLI wrapping, path relocation and newline
changes do not revoke the original CC license. No identity/email gate is added.

## Build and verify on Linux / WSL2

Use an independent environment with strict conda-forge/bioconda channel order.
`environment.release.yml` records the first reference dependency versions.
The recipe allows limited external-tool version ranges and Python 3.10–3.12;
only platforms/versions in the validation report are claimed tested.
The application materials mention Python 3.9–3.11; this release requires
3.10–3.12 as enforced by the existing CLI, so 3.9 is not advertised supported.

```bash
micromamba create -p /path/to/release-env -f environment.release.yml
micromamba run -p /path/to/release-env python -m pip install build pytest twine
micromamba run -p /path/to/release-env python -m build --outdir /path/to/work/dist
micromamba run -p /path/to/release-env python -m twine check /path/to/work/dist/*
micromamba run -p /path/to/release-env python -m pip install --no-deps /path/to/work/dist/bileactome-1.0.1-py3-none-any.whl
# Run outside the repository so the test must use installed package data.
cd /path/to/work
micromamba run -p /path/to/release-env bileactome db verify
micromamba run -p /path/to/release-env bileactome self-test --workflow all --output-dir selftest --threads 2
```

Conda build tools belong in a separate build environment / work directory:

```bash
conda build /path/to/BileActome-CLI/recipes/bileactome \
  --override-channels -c conda-forge -c bioconda \
  --croot /path/to/work/conda-build
```

When using WSL, install Linux Conda environments and its package cache on
a Linux filesystem. Some packages use symbolic links or case-sensitive
filenames that cannot be reproduced on a Windows drive mounted as DrvFS.
For this workstation, the dedicated Linux filesystem image and mount point
are both under `D:\codex-work\work\bileactome-release-20261012`; no global
WSL configuration is changed. After WSL restarts, the loop mount must be
restored before that local validation environment can be reused. Ordinary
laboratory Linux servers do not require this workstation-specific image.

The checked-in recipe uses `source: path` for local verification. It is NOT
the recipe to submit unchanged to Bioconda.

## Submission sequence

Project and collaboration contacts: Bing Wang (wangb@cau.edu.cn) and Boyan Zhang
(1362996609zby@gmail.com). Version 1.0.1 switches the original CLI framework
from the historical custom license to BSD-3-Clause to facilitate adoption.
Preserve existing 1.0.0 release assets; publish new immutable 1.0.1 assets.
Public README, licenses, CLI messages, recipe and release notes are in English.
The domestic application retains its original language and name; the English
product name is a translation for distribution.

1. Publish the exact validated source archive (`bileactome-1.0.1.tar.gz`) as
   an immutable GitHub release asset (tag `cli-v1.0.1`). PyPI publication
   remains deferred. A clearly marked CLI release avoids
   inheriting the paper repository's blanket CC BY declaration for new code.
2. Generate the public recipe from the actual archive and its public URL:

```bash
python tools/prepare_recipe.py \
  --archive /path/to/bileactome-1.0.1.tar.gz \
  --url https://github.com/1362996609zby/BileActome/releases/download/cli-v1.0.1/bileactome-1.0.1.tar.gz \
  --output /path/to/submission/recipes/bileactome/meta.yaml
```

Download the URL after publication and compare SHA-256 with the local archive.
Do not substitute the repository's `main` archive: its layout and contents
differ from the validated CLI source distribution. The CLI source archive
must also include all license texts.

3. Fork `bioconda/bioconda-recipes`, add the generated recipe under
   `recipes/bileactome/`, run Bioconda lint/build checks, and submit a PR.
   Explain the BSD-3-Clause CLI / CC-BY-4.0 resource boundary in NOTICE.
   Bioconda CI and maintainer approval are required before public availability.
4. After acceptance, test installation from the public channel in a fresh
   Linux environment and save an explicit dependency lockfile for that build.
   A local Conda build is not evidence of availability on the public channel.

Target command after acceptance (not currently available):

```bash
mamba create -n bileactome --strict-channel-priority \
  -c conda-forge -c bioconda bileactome=1.0.1
conda activate bileactome
bileactome
bileactome license
bileactome doctor
bileactome self-test --workflow all --threads 2 --output-dir selftest
```

Maintainer approval and public-channel installation verification remain
required before advertising official Bioconda availability.
