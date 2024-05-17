import os, sys; sys.path.append(os.getcwd())

import find_updates, apply_updates

app_dir = sys.argv[1]

with open(os.path.join(app_dir, "docker-compose.yml")) as f:
    contents = f.read()

images = find_updates.find_images(contents)

error = False

for image in images:
    url = image["url"]
    tag = image["tag"]
    digest = image["digest"]
    target = image["target"]
    line_no = image["line_no"]

    target_line = contents.split("\n")[line_no-1]

    image_string = f"{url}:{tag}@{digest}"

    if not apply_updates.IMAGE_UPDATE_RE.search(target_line):
        print("Error: IMAGE_UPDATE_RE did not match", file=sys.stderr)
        print(target_line, file=sys.stderr)
        error = True
        continue

    new_line = apply_updates.modify_line(target_line, image_string)

    if target_line != new_line:
        print("Error: Line modified", file=sys.stderr)
        print("From:", file=sys.stderr)
        print(target_line, file=sys.stderr)
        print("To:", file=sys.stderr)
        print(new_line, file=sys.stderr)
        error = True

if error:
    print("Test failed!")
    exit(1)
else:
    print("Test passed")

