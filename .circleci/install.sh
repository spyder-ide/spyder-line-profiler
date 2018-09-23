#!/bin/bash

export TRAVIS_OS_NAME="linux"
export CONDA_DEPENDENCIES_FLAGS="--quiet"
export CONDA_DEPENDENCIES="line_profiler mock pytest spyder pytest-cov"
export CONDA_DEPENDENCIES_FLAGS="-q"
export PIP_DEPENDENCIES="coveralls pytest-qt"

echo -e "PYTHON = $PYTHON_VERSION \n============"
git clone git://github.com/astropy/ci-helpers.git > /dev/null
source ci-helpers/travis/setup_conda_$TRAVIS_OS_NAME.sh
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

# Install the package in develop mode
pip install -e .

# Used by qthelpers to close widgets after a defined time
export TEST_CI="True"
export TEST_CI_APP="True"

# Run Spyder to get it's config files
spyder --reset
spyder
