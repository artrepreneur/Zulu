#!/bin/bash
# Run this after a new release to update dependencies

# Borrowed from https://github.com/spesmilo/electrum
# SPDX-License-Identifier: MIT

set -e

venv_dir=~/.electrum-venv
scripts=$(dirname "$0")

which virtualenv > /dev/null 2>&1 || { echo "Please install virtualenv" && exit 1; }
python3 -m hashin -h > /dev/null 2>&1 || { python3 -m pip install --user hashin; }
other_python=$(which python3)

for i in ''; do
    rm -rf "$venv_dir"
    python3 -m venv $venv_dir

    source $venv_dir/bin/activate

    echo "Installing $m dependencies with $(which python)"

    python -m pip install -r $scripts/../requirements${i}.txt --upgrade

    echo "OK."

    requirements=$(pip freeze --all)
    restricted=$(echo $requirements | $other_python $scripts/deterministic-build/find_restricted_dependencies.py)
    requirements="$requirements $restricted"

    echo "Generating package hashes..."
    rm $scripts/deterministic-build/requirements${i}.txt || true
    touch $scripts/deterministic-build/requirements${i}.txt

    for requirement in $requirements; do
        echo -e "\r  Hashing $requirement..."
        $other_python -m hashin -r "$scripts/deterministic-build/requirements${i}.txt" "${requirement}"
    done

    echo "OK."
done

echo "Done. Updated requirements"