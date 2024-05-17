#!/bin/env bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ -d /tmp/umbrel-apps ]; then
    echo "Repository exists"
else
    git clone https://github.com/getumbrel/umbrel-apps /tmp/umbrel-apps

    pushd /tmp/umbrel-apps
    git remote add target git@github.com:highghlow/umbrel-apps
    popd
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
    branch_name="autoupdate-$app_id"

    mkdir -p $app_dir

    git switch master
    git branch -c $branch_name || echo "autoupdate-$app_id already exists"
    git switch $branch_name

    python3 $SCRIPT_DIR/find_updates.py $app_id/docker-compose.yml > $app_dir/update

    cat $app_dir/update

    update_count=$(cat $app_dir/update | wc -l)
    main_update=$(cat $app_dir/update | tail -1)
    echo Applying $update_count updates

    cat $app_dir/update | python3 $SCRIPT_DIR/apply_updates.py $app_id/docker-compose.yml

    echo Applied $update_count updates
    
    if [ $update_count -eq 0 ]; then
	echo "$app_id is up to date"
	return
    fi

    git add $app_id
    git commit -m "Updated Immich: $main_update"
    git push --set-upstream target $branch_name
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
