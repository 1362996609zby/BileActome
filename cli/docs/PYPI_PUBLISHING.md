# PyPI publication of BileActome CLI 1.0.0

The project is prepared for PyPI Trusted Publishing. A PyPI account owner
must configure the pending publisher before the GitHub workflow is run.
No password or API token is stored in this repository.

## One-time account configuration

Sign in to https://pypi.org/ and enable the account's required two-factor
authentication. Open https://pypi.org/manage/account/publishing/ and add a
pending GitHub publisher with these exact values:

| Field | Value |
| --- | --- |
| PyPI project name | `bileactome` |
| GitHub owner | `1362996609zby` |
| Repository | `BileActome` |
| Workflow filename | `pypi-publish.yml` |
| Environment | `pypi` |

The PyPI account that creates the pending publisher becomes the initial
project owner on successful first publication. This is package-index
administration, not a transfer of the software's copyright.

## Release procedure

Run the **Publish validated CLI release to PyPI** workflow manually from
the repository's Actions tab after account configuration. The workflow
downloads the published CLI 1.0.0 wheel and source archive, verifies both
fixed SHA256 checksums, runs strict Twine metadata validation, and passes
the exact files to a separate OIDC-authenticated publishing job. No new
build, package token, version change, or license change is involved.

The workflow has no automatic push trigger. Its `pypi` environment must
match the PyPI publisher configuration. Adding environment approval
requirements is optional and will require an authorized reviewer to
approve each deployment before publication.

After successful publication:

1. Confirm https://pypi.org/project/bileactome/1.0.0/ exists.
2. Compare the PyPI JSON file checksums with the GitHub release files.
3. Install from the public index in an isolated Linux environment and run
   `bileactome --version`, `bileactome db verify`, and the bundled self-tests.
4. Update the homepage to say published only after these checks pass.

Do not replace already published version 1.0.0 files. A substantive package
change requires a new version. Repository documentation can be updated
without altering the immutable installation artifacts.

## Installation after publication

```bash
mamba create -n bileactome-pip --strict-channel-priority -c conda-forge -c bioconda python=3.11 pip 'bash>=4' 'hmmer>=3.4,<3.5' 'prodigal>=2.6.3,<2.7' 'bowtie2>=2.5.4,<2.6'
conda activate bileactome-pip
python -m pip install bileactome==1.0.0
bileactome doctor --workflow all
bileactome db verify
bileactome self-test --workflow all
```

`pip` installs the Python package and its Python dependencies, not HMMER,
Prodigal, Bowtie2, or Bash. Linux is the supported and validated workflow
platform. The package includes all 27 HMMs and toy fixtures. Licensing and
commercial contacts remain those in LICENSE and NOTICE; PyPI publication
does not change them. Bioconda review is a separate process.
