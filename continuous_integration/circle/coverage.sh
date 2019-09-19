#!/bin/bash

export COVERALLS_REPO_TOKEN="NFNNbVsb3wb3uBRYljg96R74lRiRRePIU"
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

coveralls
