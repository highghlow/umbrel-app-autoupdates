import sys, requests

BODY="""This pull request was automatically created by the [Umbrel Updater Bot](https://github.com/highghlow/umbrel-app-autoupdates)

If there is an issue, you can stop the bot by [creating a halt issue](https://github.com/highghlow/umbrel-app-autoupdates/issues/new?assignees=highghlow&labels=bug%2C+critical&projects=&template=stop-this-program.md&title=HALT%3A+%3Creason%3E)

NOTE: You will have to update the release notes manually"""


def create_pr(app, source_owner, branch_name, target_repo, main_update, token):
    TITLE = f"Update: {app.title()} {main_update}"

    print("Creating a pull request...")
    response = requests.post(f"https://api.github.com/repos/{target_repo}/pulls", json={
        "title": TITLE,
        "body": BODY,
        "head": f"{source_owner}:{branch_name}",
        "base": "master"
    }, headers={
        "Authorization": f"Bearer {token}"
    })

    pr_already_exists = False
    if response.status_code == 422:
        errors = response.json()["errors"]
        if len(errors) == 1 and errors[0]["message"].startswith("A pull request already exists"):
            pr_already_exists = True
            print(errors[0]["message"])

    if not pr_already_exists:
        response.raise_for_status()
    else:
        response = requests.get(f"https://api.github.com/repos/{target_repo}/pulls?state=open&base=master&head={source_owner}:{branch_name}")
        response.raise_for_status()

        prs = response.json()
        if len(prs) != 1:
            raise Exception(f"Unexpected numbrel of PRs: {len(prs)}")
        pr_number = prs[0]["number"]
        existing_title = prs[0]["title"]
        existing_body = prs[0]["body"]

        if existing_title == TITLE and existing_body == BODY:
            print("PR Update not needed")
            return

        print(f"Updating PR#{pr_number}...")

        requests.patch(
                f"https://api.github.com/repos/{target_repo}/pulls/{pr_number}",
                json = {
                    "title": TITLE,
                    "body": BODY
                },
                headers = {
                    "Authorization": f"Bearer {token}"
                }
        ).raise_for_status()

if __name__ == "__main__":
    _, app, source_owner, branch_name, target_repo, main_update, token = sys.argv
    create_pr(app, source_owner, branch_name, target_repo, main_update, token)
