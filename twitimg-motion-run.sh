#!/usr/bin/env bash

set -euxo pipefail

SCRIPT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
photo_dir="/mnt/ramdisk_motion"

python3 -m venv "${SCRIPT_DIR}"/venv3
# shellcheck source=/dev/null
source "${SCRIPT_DIR}"/venv3/bin/activate
pip install -r "${SCRIPT_DIR}"/requirements.txt
python "${SCRIPT_DIR}"/tweet_motion_jpg.py "${photo_dir}"
