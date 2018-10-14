#!/bin/bash
set -ex

# collect posargs
envbindir=$1
toxinidir=$2

# purge previous build artifacts
rm -rf ./dist

# build & install package
poetry install -v
poetry build -f wheel

pkg_name=$(ls ./dist | grep .whl)
${envbindir}/pip install -U ${toxinidir}/dist/${pkg_name}
