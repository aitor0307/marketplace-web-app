#!/usr/bin/env bash
# Run Flask-Migrate (Alembic) commands against the VM's database.
#
# Lives on the VM as /opt/marketplace/migrate.sh. Runs in a one-off container
# from the current `app` image (that's where the migration files are), with the
# same app.env/db.env as the app, and without starting Redis (--no-deps).
#
# Usage:
#   ./migrate.sh                     # flask db upgrade
#   ./migrate.sh --pull              # pull the latest app image first, then upgrade
#   ./migrate.sh current             # any other `flask db` command, e.g.
#   ./migrate.sh heads | history | downgrade <revision>
#   ./migrate.sh --pull current      # --pull combines with any command
set -euo pipefail

APP_DIR=/opt/marketplace

# Every docker command on the VM needs root.
if [ "$(id -u)" -ne 0 ]; then
  exec sudo "$0" "$@"
fi

pull=false
if [ "${1:-}" = "--pull" ]; then
  pull=true
  shift
fi

# No arguments = upgrade to the latest revision.
if [ "$#" -eq 0 ]; then
  set -- upgrade
fi

cd "$APP_DIR"

if [ "$pull" = true ]; then
  echo "==> Pulling the latest app image"
  docker compose pull app
fi

echo "==> flask db $*"
# The minimal Alembic factory, so a missing SMTP/Redis/OAuth setting can't
# block a migration (see app/__init__alembic.py).
docker compose run --rm --no-deps -T \
  -e FLASK_APP=app/__init__alembic.py \
  app flask db "$@"
