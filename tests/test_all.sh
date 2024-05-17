#!/bin/env bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ -d /tmp/umbrel-apps ]; then
    echo "Repository exists"
else
    git clone https://github.com/getumbrel/umbrel-apps /tmp/umbrel-apps
    git remote add target git@github.com:highghlow/umbrel-apps
fi

for app in /tmp/umbrel-apps/*; do
    appname=$(basename $app)
    if [[ $appname == "README.md" ]]; then
	sleep 0
    else
	python3 $SCRIPT_DIR/test_image_finding_regex.py $app > /dev/null || echo "Failed (image_finding_regex): $appname"
	python3 $SCRIPT_DIR/test_replacement_preservation.py $app > /dev/null || echo "Failed (replacement_preservation): $appname"
    fi
done
