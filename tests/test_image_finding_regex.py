import os, sys; sys.path.append(os.getcwd())

import find_updates

app_dir = sys.argv[1]

with open(os.path.join(app_dir, "docker-compose.yml")) as f:
    contents = f.read()

search_count = 0
regex_count = 0

for ind, line in enumerate(contents.split("\n")):
    search = (line.find("image:") != -1) and (line.find("noupdate:") == -1)
    regex = bool(find_updates.IMAGE_RE.match(line))

    if search: search_count += 1
    if regex: regex_count += 1

    if search != regex:
        print(f"Verdict mismatch! Search: {search}, Regex: {regex}", file=sys.stderr)
        print(f"{ind+1}: {line}", file=sys.stderr)

if search_count != regex_count:
    print("Test failed!", file=sys.stderr)
    exit(1)
else:
    print("Test passed")
