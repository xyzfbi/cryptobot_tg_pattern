#!/bin/bash
# shellcheck disable=SC2164
cd "$(dirname "$0")"
export PYTHONPATH="$PWD"
# repo url to clone
REPO_URL="https://github.com/xyzfbi/cryptobot_tg_pattern"
REPO_DIR="cryptobot_tg"

# check if anaconda exists
if ! command -v conda >/dev/null 2>&1; then
    if [ -d "$HOME/miniconda3" ]; then
        CONDA="$HOME/miniconda3"
    elif [ -d "$HOME/anaconda3" ]; then
        CONDA="$HOME/anaconda3"
    else
        echo "ERROR: Conda not found. Please install Miniconda or Anaconda."
        exit 1
    fi
    source "$CONDA/etc/profile.d/conda.sh"
else
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi

# check for git
if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: Git is not installed. Please install Git."
    exit 1
fi

# MODULE CLOINNNNG REPO
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning repository from $REPO_URL"
    git clone "$REPO_URL" "$REPO_DIR"
    # shellcheck disable=SC2181
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to clone repository."
        exit 1
    fi
else
    echo "Repository already exists in $REPO_DIR"
fi

# GO INTO REPO DIR
cd "$REPO_DIR" || {
    echo "ERROR: Failed to change directory to $REPO_DIR"
    exit 1
}
export PYTHONPATH="$PWD"

# MODULE CREATING CONDA ENVIRONMENT
if ! conda env list | grep -q "cryptobot_tg"; then
    echo "Creating Conda environment 'cryptobot_tg' from environment.yml"
    conda env create -f environment.yml
    # shellcheck disable=SC2181
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create Conda environment."
        exit 1
    fi
else
    echo "Environment 'cryptobot_tg' already exists"
fi
conda activate cryptobot_tg
# MODULE ACTIVATING CONDA ENVIRONMENT
# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate Conda environment 'cryptobot_tg'."
    exit 1
fi

# MODULE RUN MAIN.PY
python main.py
# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run main.py."
    exit 1
fi

# shellcheck disable=SC2162
read -p "Press Enter to continue..."