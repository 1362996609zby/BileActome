#!/usr/bin/env bash
# Inputs: conda-build environment, source tree, dedicated work directory.
# Outputs: local Conda artifact and conda-build's installed-package test log.
set -euo pipefail
build_env=${1:?Usage: validate_conda.sh ENV_DIR SOURCE_DIR WORK_DIR}
build_source=${2:?Missing SOURCE_DIR}
build_work=${3:?Missing WORK_DIR}
mkdir -p "$build_work"
export PATH="$build_env/bin:$PATH"
export TMPDIR="${RELEASE_TMPDIR:-$build_work/tmp}"
export CONDA_PKGS_DIRS="$build_work/conda-pkgs"
export CONDA_ENVS_PATH="$build_work/conda-envs"
export CONDARC="$build_work/condarc"
export PYTHONPYCACHEPREFIX="$build_work/pycache"
export BILEACTOME_NO_BANNER=1
mkdir -p "$TMPDIR" "$CONDA_PKGS_DIRS" "$CONDA_ENVS_PATH"
recipe_source=$(mktemp -d "$build_work/recipe-source-XXXXXX")
cp -a "$build_source/." "$recipe_source/"
cd "$build_work"
conda build "$recipe_source/recipes/bileactome" --no-anaconda-upload \
  --override-channels -c conda-forge -c bioconda \
  --croot "$build_work/conda-build" > "$build_work/conda-build.log" 2>&1
printf '%s\n' 'Local Conda build and installed-package recipe tests passed.'
