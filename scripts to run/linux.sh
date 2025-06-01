#!/bin/bash
# shellcheck disable=SC2164
cd "$(dirname "$0")"
export PYTHONPATH="$PWD"

REPO_URL="https://github.com/xyzfbi/cryptobot_tg_pattern"
REPO_DIR="cryptobot_tg"

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

if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: Git is not installed. Please install Git."
    exit 1
fi

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

cd "$REPO_DIR" || {
    echo "ERROR: Failed to change directory to $REPO_DIR"
    exit 1
}
export PYTHONPATH="$PWD"

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
# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate Conda environment 'cryptobot_tg'."
    exit 1
fi

python main.py
# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run main.py."
    exit 1
fi

# shellcheck disable=SC2162
read -p "Press Enter to continue..."