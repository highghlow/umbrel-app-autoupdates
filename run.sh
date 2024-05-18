#!/bin/env bash
set -euo pipefail

TARGET_REPO="highghlow/umbrel-apps" # TODO: Change to getumbrel/umbrel-apps
SOURCE_REPO="highghlow/umbrel-apps"
SOURCE_OWNER=$(dirname $SOURCE_REPO)

echo $GITHUB_TOKEN > /dev/null

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if curl -s https://api.github.com/repos/highghlow/umbrel-app-autoupdates/issues | grep "\"title\": \"HALT"; then
    echo "Error: HALT issue found"
    exit 1
fi

if [ -d /tmp/umbrel-apps ]; then
    echo "Repository exists"
else
    git clone https://github.com/getumbrel/umbrel-apps /tmp/umbrel-apps

    pushd /tmp/umbrel-apps
    git remote add target git@github.com:$SOURCE_REPO
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

    main_update=$(cat $app_dir/update | tail -1)

    cat $app_dir/update | python3 $SCRIPT_DIR/apply_updates.py $app_id/docker-compose.yml

    if [[ $(cat $app_dir/update) ]]; then
	true
    else
	echo "$app_id is up to date"
	return
    fi

    git add $app_id
    git commit -m "Updated Immich: $main_update"
    git push --set-upstream target $branch_name

    title="Test: Update: Immich $main_update"
    body="This is an automatic process\n\nIf there is an error, create an issue on https://github.com/highghlow/umbrel-app/autoupdates and don't touch this PR.\nIf you close it, another one will be created"

    response=$(curl -s https://api.github.com/repos/$TARGET_REPO/pulls --data "{
	\"title\": \"$title\",
	\"body\": \"$body\",
	\"head\": \"$SOURCE_OWNER:$branch_name\",
	\"base\": \"master\"
    }" -H "Authorization: Bearer $GITHUB_TOKEN")

    if echo "$response" | grep "A pull request already exists"; then
	echo "Updating existing pull request"
	pr_number=$(curl -s "https://api.github.com/repos/$TARGET_REPO/pulls?state=open&base=master&head=$SOURCE_OWNER:$branch_name" | jq -r '.[0].number')
	echo "PR: $TARGET_REPO/$pr_number"

	url="https://api.github.com/repos/$TARGET_REPO/pulls/$pr_number"
	curl -L \
	    -X PATCH \
	    -H "Accept: application/vnd.github+json" \
	    -H "Authorization: Bearer $GITHUB_TOKEN" \
	    $url \
	    -d "{\"title\": \"$title\", \"body\":\"$body\"}" > /dev/null
    fi
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
