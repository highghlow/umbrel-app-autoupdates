import functools
import requests

HOST = "index.docker.io"

def get_repo(url):
    if "/" not in url:
        url = "library/"+url
    return url

def get_token(repo):
    url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
    response = requests.get(url)
    response.raise_for_status()
    json = response.json()
    return json["token"]

