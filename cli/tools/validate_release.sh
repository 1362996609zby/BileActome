#!/usr/bin/env bash
# Inputs: installed release environment, project source, dedicated work path.
# Outputs: distributions, test logs, self-test results and explicit env lock.
set -euo pipefail
release_env=${1:?Usage: validate_release.sh ENV_DIR SOURCE_DIR WORK_DIR}
release_source=${2:?Missing SOURCE_DIR}
release_work=${3:?Missing WORK_DIR}
mkdir -p "$release_work/dist" "$release_work/tmp" "$release_work/run"
export PATH="$release_env/bin:$PATH"
export TMPDIR="${RELEASE_TMPDIR:-$release_work/tmp}"
mkdir -p "$TMPDIR"
export PYTHONPYCACHEPREFIX="$release_work/pycache"
export PIP_CACHE_DIR="$release_work/pip-cache"
export BILEACTOME_NO_BANNER=1
# Build only in the work area: setuptools writes build/ and egg-info here.
build_source=$(mktemp -d "$release_work/build-source-XXXXXX")
cp -a "$release_source/." "$build_source/"
cd "$build_source"
python -m build --no-isolation --outdir "$release_work/dist" > "$release_work/build.log" 2>&1
python -m twine check "$release_work"/dist/* > "$release_work/twine.log" 2>&1
package_version=$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
python -m pip install --no-deps --force-reinstall "$release_work/dist/bileactome-${package_version}-py3-none-any.whl" > "$release_work/install.log" 2>&1
cd "$release_work/run"
python -m pytest "$release_source/tests" -q --capture=sys -o cache_dir="$release_work/pytest-cache" > "$release_work/pytest.log" 2>&1
bileactome --version > "$release_work/version.txt"
bileactome --banner --help > "$release_work/help.txt" 2> "$release_work/logo.txt"
bileactome license > "$release_work/license.txt"
bileactome db verify > "$release_work/database.json"
bileactome doctor --json "$release_work/doctor.json" > "$release_work/doctor.txt"
bileactome self-test --workflow all --threads 2 --output-dir "$release_work/selftest" > "$release_work/selftest.json" 2> "$release_work/selftest.log"
bileactome self-test --workflow all --threads 2 --output-dir "$release_work/selftest" > "$release_work/selftest-resume.json" 2> "$release_work/selftest-resume.log"
printf '%s\n' 'Wheel build, metadata, unit tests, 27 HMMs, MAG/catalog self-test and resume passed.'
