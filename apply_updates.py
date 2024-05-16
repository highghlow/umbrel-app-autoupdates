import re
import sys

IMAGE_UPDATE_RE = re.compile(r"(?<=image: )[a-zA-Z0-9./_-]*:[0-9a-z.-]*@sha256:[a-z0-9]{64}") # We can be more lenient here since most fintering is happening in `find_updates`

def apply_updates(file, updates):
    with open(file) as f:
        contents = f.read()

    for line, image in updates:
        contents = apply_update(contents, line, image)

    with open(file, "w") as f:
        f.write(contents)

def apply_update(contents, line, image):
    lines = contents.split("\n")

    lines[line-1] = IMAGE_UPDATE_RE.sub(image, lines[line-1])

    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    updates_raw = sys.stdin.read().split("\n")[:-1]
    updates = []
    for update_line in updates_raw:
        print(repr(update_line))
        line, image = update_line.split(": ", maxsplit=1)
        line = int(line)
        updates.append((line, image))

    apply_updates(file, updates)
