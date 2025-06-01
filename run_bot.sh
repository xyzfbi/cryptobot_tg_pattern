#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PWD
source "$(conda info --base)/etc/profile.d/conda.sh"

if ! conda env list | grep -q "cryptobot_tg"; then
    echo "Creating Conda environment 'cryptobot_tg' from environment.yml"
    conda env create -f environment.yml
else
    echo "Environment 'cryptobot_tg' already exists"
fi

conda activate cryptobot_tg

python main.py