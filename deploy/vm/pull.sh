#!/usr/bin/env bash
# Pull the newest app + frontend images from Artifact Registry.
#
# Lives on the VM as /opt/marketplace/pull.sh. Only downloads: nothing is
# restarted, so run migrate.sh and then `docker compose up -d` afterwards.
#
# Usage:
#   ./pull.sh               # app and frontend
#   ./pull.sh frontend      # just one service
set -euo pipefail

APP_DIR=/opt/marketplace

# Every docker command on the VM needs root.
if [ "$(id -u)" -ne 0 ]; then
  exec sudo "$0" "$@"
fi

if [ "$#" -eq 0 ]; then
  set -- app frontend
fi

cd "$APP_DIR"

echo "==> Pulling: $*"
docker compose pull "$@"

# What was just downloaded (not what the running containers use: those keep
# their old image until recreated). "Created" is when the image was built.
echo "==> Pulled images"
docker compose config --images "$@" | while read -r image; do
  docker image ls "$image" --format '{{.Repository}}:{{.Tag}}  built {{.CreatedSince}}  id {{.ID}}'
done
