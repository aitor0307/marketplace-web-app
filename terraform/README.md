# Marketplace infrastructure (GCP)

Each environment is one Compute Engine VM that runs:

- **PostgreSQL** installed on the host (not a container)
- **Docker Compose** with the app container, the React frontend container and Redis
- **nginx** on the host on ports 80 and 443: `/api/` and `/static/` go to the app on `127.0.0.1:8000`, everything else to the frontend on `127.0.0.1:8080`

```
live/
  common.hcl        # credentials file, project, region, state bucket  <- edit this one
  root.hcl          # GCS remote state + generated google provider
  dev/terragrunt.hcl
  prod/terragrunt.hcl
modules/marketplace-vm/
  templates/startup.sh.tftpl          # sets up the VM on every boot
  templates/docker-compose.yml.tftpl  # app + frontend + redis
  templates/nginx.conf.tftpl
```

## Credentials

`live/common.hcl` points to the service-account key. On a different machine, override it without editing any file:

```bash
export GOOGLE_CREDENTIALS_FILE=/path/to/key.json
export GOOGLE_PROJECT=my-project   # optional; the default is ceva-cloud
```

The service account needs permission to create Compute, Artifact Registry, IAM service accounts and project IAM bindings, and to enable services. Owner or Editor plus Project IAM Admin is enough.

## Deploy

```bash
cd live/dev     # or live/prod
terragrunt init
terragrunt plan
terragrunt apply
```

The first run creates the state bucket. Outputs include `public_ip`, `ssh_command` and `artifact_registry`.

### Ship the app

```bash
REPO=$(terragrunt output -raw artifact_registry)
gcloud auth configure-docker "${REPO%%/*}"
docker build -f docker/Dockerfile -t "$REPO/app:latest" .   # from the repo root
docker push "$REPO/app:latest"
# VITE_API_URL empty = the SPA calls the API same-origin through the VM's nginx
docker build -f frontend/Dockerfile.ci -t "$REPO/frontend:latest" frontend
docker push "$REPO/frontend:latest"

# on the VM (see the ssh_command output)
cd /opt/marketplace
sudo nano app.env                                   # mail, OAuth, FRONTEND_URL, ...
sudo docker compose pull && sudo docker compose up -d
sudo docker compose run --rm app flask --app 'app.__init__alembic:create_app' db upgrade
```

## How the VM is laid out

- A separate persistent disk is mounted at `/mnt/data`. It holds Postgres (`/var/lib/postgresql` and `/etc/postgresql`), Docker volumes (`/var/lib/docker`) and `/opt/marketplace`. Replacing the VM keeps all of this data. The disk gets a daily snapshot (3 days kept in dev, 14 in prod).
- The Postgres password is generated on the VM the first time it boots. It is saved in `/mnt/data/secrets/postgres_password` and written into `/opt/marketplace/db.env` as `DATABASE_URL`. It is never stored in Terraform state.
- Only ports 80 and 443 are open to the internet. SSH is allowed only through IAP (`--tunnel-through-iap`) with OS Login. Postgres and Redis are not reachable from outside the VM.
- **TLS:** set `domain` and `letsencrypt_email` in the environment's `terragrunt.hcl`, point DNS at `public_ip`, apply, and reboot. certbot then obtains the certificate and sets up the redirect to HTTPS.
- **Changing a template:** after `terragrunt apply`, either reboot the VM or run `sudo google_metadata_script_runner startup`. The script is idempotent. Log: `/var/log/marketplace-startup.log`.
