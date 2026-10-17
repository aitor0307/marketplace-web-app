#!/usr/bin/env bash
# Runs ON the VM, as root: deploy.yml pipes it through
#   gcloud compute ssh ... --command "sudo bash -s" < this file
# /opt/marketplace and its docker-compose.yml are written by the VM's startup
# script (terraform/modules/marketplace-vm/templates/startup.sh.tftpl), which
# also configures root's docker to pull from Artifact Registry.
set -euo pipefail

APP_DIR=/opt/marketplace
HEALTH_TIMEOUT_SECONDS=180

cd "$APP_DIR"

echo "==> Pulling images"
docker compose pull app frontend

echo "==> Running database migrations"
# The minimal Alembic factory, so a missing SMTP/Redis/OAuth setting can't
# block a migration (see app/__init__alembic.py).
docker compose run --rm -T -e FLASK_APP=app/__init__alembic.py app flask db upgrade

echo "==> Restarting containers"
docker compose up -d --remove-orphans

echo "==> Waiting for the app to report healthy"
app_container="$(docker compose ps -q app)"
deadline=$((SECONDS + HEALTH_TIMEOUT_SECONDS))
status=""
while [ "$SECONDS" -lt "$deadline" ]; do
  status="$(docker inspect --format '{{.State.Health.Status}}' "$app_container")"
  [ "$status" = "healthy" ] && break
  sleep 5
done

if [ "$status" != "healthy" ]; then
  echo "App is '$status' after ${HEALTH_TIMEOUT_SECONDS}s; last logs:" >&2
  docker compose logs --tail 100 app >&2
  exit 1
fi

echo "==> Pruning old images"
docker image prune -f

echo "==> Deployed"
docker compose ps
