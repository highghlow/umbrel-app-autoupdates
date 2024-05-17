#!/bin/env bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ -d /tmp/umbrel-apps ]; then
    echo "Repository exists"
else
    git clone https://github.com/getumbrel/umbrel-apps /tmp/umbrel-apps
    git remote add target git@github.com:highghlow/umbrel-apps
fi

pushd /tmp/umbrel-apps
if [[ $(git diff) ]]; then
    echo "Error: Uncommited changes in umbrel-apps"
    exit 1
fi

update_app() {
    app_id=$1
    app_dir=/tmp/umbrel-updater/$app_id
    umbrel_apps=$(pwd)

    mkdir -p $app_dir

    git branch -c autoupdate-$app_id || echo "autoupdate-$app_id already exists"
    git switch autoupdate-$app_id

    python3 $SCRIPT_DIR/find_updates.py $app_id/docker-compose.yml > $app_dir/update

    cat $app_dir/update

    update_count=$(cat $app_dir/update | wc -l)
    echo Applying $update_count updates

    cat $app_dir/update | python3 $SCRIPT_DIR/apply_updates.py $app_id/docker-compose.yml

    echo Applied $update_count updates
    
    if [ $update_count -eq 0 ]; then
	echo "$app_id is up to date"
	return
    fi

    # python3 $SCRIPT_DIR/generate_pr_message.py > $app_dir/pr-message
}

if [ $# -ne 0 ]; then
    update_app $1
else
    for app in *; do
	if [[ $app == "README.md" ]]; then
	    sleep 0
	else
	    update_app $app || echo "$app update failed"
	fi
    done
fi

popd
