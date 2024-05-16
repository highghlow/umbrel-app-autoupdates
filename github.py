import functools
import requests

HOST = "ghcr.io"

@functools.lru_cache()
def get_repo(url):
    return url[8:] # remove ghcr.io/

def get_token(repo):
    url = f"https://ghcr.io/token?scope=repository:{repo}:pull"
    response = requests.get(url)
    response.raise_for_status()
    json = response.json()
    return json["token"]

