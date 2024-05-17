import re
import sys

IMAGE_UPDATE_RE = re.compile(r"^([ ]*image: \"?).*@sha256:[a-f0-9]{64}(\"?.*)") # We can be more lenient here since most fintering is happening in `find_updates`

def apply_updates(contents, updates):
    for line, image in updates:
        contents = apply_update(contents, line, image)

def apply_update(contents, line, image):
    lines = contents.split("\n")

    lines[line-1] = modify_line(lines[line-1], image)

    return "\n".join(lines)

def modify_line(line, text):
    return IMAGE_UPDATE_RE.sub(r"\1"+text+r"\2", line)

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    updates_raw = sys.stdin.read().split("\n")[:-1]
    updates = []
    for update_line in updates_raw:
        line, image = update_line.split(": ", maxsplit=1)
        line = int(line)
        updates.append((line, image))

    with open(file) as f:
        contents = f.read()

    apply_updates(contents, updates)

    with open(file, "w") as f:
        f.write(contents)
