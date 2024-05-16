import docker

import github
import docker_hub

import re

IMAGE_RE = re.compile(r"^[ ]*image: (?P<url>\w*(?:\.\w*)*(?:/[^: ]*)*):(?P<tag>[0-9a-z.-]*)@sha256:(?P<digest>[a-z0-9]{64})[ ]*(?:#[ ]*target:[ ]*(?P<target>[a-zA-Z0-9]*))?$", re.MULTILINE) # I know that this is cursed. Just plop in into regex101.com to see what it's doing (Select Python on the left)

def find_updates(docker_compose):
    with open(docker_compose) as f:
        contents = f.read()

    images = find_images(contents)
    updates = []
    for image in images:
        url = image["url"]
        tag_current = image["tag"]
        digest = image["digest"]
        target = image["target"]

        if not target:
            target = "latest"

        if url.startswith("ghcr.io"):
            service = github
        else:
            service = docker_hub

        repo = service.get_repo(url)
        token = service.get_token(repo)
        host = service.HOST

        print(f"Checking for updates: {host}/{repo}")

        tag_latest, digest_latest = docker.get_latest_tag(host, repo, tag_current, target, token)

        if digest_latest != digest:
            updates.append((tag_latest, digest_latest))

    return updates

def find_images(text):
    images = []
    for match in IMAGE_RE.finditer(text):
        url, tag, digest, target = match.groups()
        images.append({"url": url, "tag": tag, "digest": digest, "target": target})
    return images

if __name__ == "__main__":
    import sys
    print(find_updates(sys.argv[1]))
