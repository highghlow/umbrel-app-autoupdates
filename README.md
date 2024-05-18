# Umbrel Autoupdater
_Automatically starts pull requests for app updates in https://github.com/getumbrel/umbrel-apps_

## Explanation

In every apps' docker-compose file this bot searches for lines matching this signature:
```yaml
image: <image>:<tag>@sha256:<digest> [# target: <target-tag>] [#!]
```

### Target
The target tag is the tag you want to track. So, for example if on each release you push a new image to the `release` tag (as well as a `v<version>` tag), you would specify `target: release`

### Main update
The `#!` comment mark an image as the main one. This is needed if your app uses additional containers (like databases). If you don't mark the main image, the updater could update your app from `postgres-11` to `postgres-12`. By default the last image is concidered to be the main one.
