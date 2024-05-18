import re
import sys
import os

IMAGE_UPDATE_RE = re.compile(r"^([ ]*image: \"?).*@sha256:[a-f0-9]{64}(\"?.*)") # We can be more lenient here since most fintering is happening in `find_updates`

def apply_updates(contents, updates):
    for line, image in updates:
        contents = apply_update(contents, line, image)
    return contents

def apply_update(contents, line, image):
    lines = contents.split("\n")

    lines[line-1] = modify_line(lines[line-1], image)

    return "\n".join(lines)

def modify_line(line, text):
    return IMAGE_UPDATE_RE.sub(r"\1"+text+r"\2", line)

def update_manifest(contents, main_update):
    from_, to = main_update

    return contents.replace(from_, to)

if __name__ == "__main__":
    import sys
    app_dir = sys.argv[1]
    docker_compose = os.path.join(app_dir, "docker-compose.yml")
    app_manifest = os.path.join(app_dir, "umbrel-app.yml")

    updates_raw = sys.stdin.read().split("\n")[:-1] # Main update + trailing newline
    main_update = updates_raw[-1].split(" -> ")
    updates_raw = updates_raw[:-1]

    updates = []
    for update_line in updates_raw:
        print(repr(update_line))
        line, image = update_line.split(": ", maxsplit=1)
        line = int(line)
        updates.append((line, image))



    with open(docker_compose) as f:
        contents = f.read()

    contents = apply_updates(contents, updates)

    with open(docker_compose, "w") as f:
        f.write(contents)


    with open(app_manifest) as f:
        contents = f.read()

    contents = update_manifest(contents, main_update)

    with open(app_manifest, "w") as f:
        f.write(contents)
