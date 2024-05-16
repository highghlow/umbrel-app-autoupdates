import requests
import functools
import re

import urllib.parse
urljoin = urllib.parse.urljoin

LINK_RE = re.compile("<(.*)>; rel=[\"]next[\"]")

@functools.lru_cache()
def get_latest_tag(host, repo, current, target, token):
    tags = get_tags(host, repo, token)
    print(f"Got {len(tags)} tags")

    if target not in tags:
        raise ValueError(f"Target tag ({target}) wasn't found in {repo}")

    target_digest = get_digest(host, repo, target, token)
    print(f"Target digest ({target}):", target_digest)

    current_digest = get_digest(host, repo, current, token)
    print(f"Current digest: ({current})", current_digest)

    update_tag = None
    if current_digest != target_digest:
        print("Digests don't match. Updating...")
        for tag in reversed(tags):
            print(f"Trying {tag}...")
            if tag == target: continue

            new_digest = get_digest(host, repo, tag, token)
            if new_digest == target_digest:
                update_tag = tag
                print(f"Update found: {update_tag}")
                break

    if not update_tag:
        raise Exception("Update required, but not found")

    return update_tag, target_digest

@functools.lru_cache()
def get_digest(host, repo, tag, token):
    response = requests.head(f"https://{host}/v2/{repo}/manifests/{tag}",
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Accept": "application/vnd.oci.image.index.v1+json"
                            })
    response.raise_for_status()
    return response.headers["docker-content-digest"]

@functools.lru_cache()
def get_tags(host, repo, token, manual_url=None):
    if manual_url:
        url = manual_url
    else:
        url = f"https://{host}/v2/{repo}/tags/list?n=1000"

    response = requests.get(url, 
                            headers={
                                f"Authorization": f"Bearer {token}"
                            })
    print(response.text)
    response.raise_for_status()
    json = response.json()
    tags = json["tags"]

    if "Link" in response.headers.keys():
        print("New page")
        href = LINK_RE.match(response.headers["Link"]).groups()[0]
        next_page = urljoin(url, href)
        tags += get_tags(host, None, token, next_page)

    return tags


