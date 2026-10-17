# Deployment runbook

Manual build/push/rollout. On `master`, `.github/workflows/deploy.yml` does all
of this automatically (dev on push, prod via "Run workflow"); use these
commands when deploying by hand or debugging.

## Targets

Images go to Artifact Registry, in the repo terraform creates per environment
(`terraform/modules/marketplace-vm`):

| Env  | Region         | Zone             | Registry                                                  | VM                    |
|------|----------------|------------------|-----------------------------------------------------------|-----------------------|
| dev  | `us-central1`  | `us-central1-a`  | `us-central1-docker.pkg.dev/<gcp-project>/marketplace-dev`   | `marketplace-dev-vm`  |
| prod | `europe-west4` | `europe-west4-a` | `europe-west4-docker.pkg.dev/<gcp-project>/marketplace-prod` | `marketplace-prod-vm` |

The VM's `docker-compose.yml` pulls `app:latest` and `frontend:latest`.

## 1. Variables

Run everything from the repo root.

```bash
cd path/to/marketplace-web-app

export GCP_PROJECT=my-gcp-project       # FILL IN
export GCP_REGION=us-central1         # prod: europe-west4
export GCP_ZONE=us-central1-a         # prod: europe-west4-a
export AR_REPO=marketplace-dev        # prod: marketplace-prod
export REGISTRY=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${AR_REPO}
export TAG=$(git rev-parse --short HEAD)
export GCP_KEY=/path/to/service-account-key.json   # FILL IN
```

## 2. Build the images (local)

Builds and tags the images on your machine; nothing is uploaded yet.

### Backend (`app`)

```bash
docker build --platform linux/amd64 \
  -f docker/Dockerfile \
  -t ${REGISTRY}/app:${TAG} -t ${REGISTRY}/app:latest \
  .
```

### Frontend

```bash
docker build --platform linux/amd64 \
  -f frontend/Dockerfile \
  --build-arg VITE_API_URL= \
  --build-arg VITE_ENVIRONMENT=production \
  -t ${REGISTRY}/frontend:${TAG} -t ${REGISTRY}/frontend:latest \
  frontend
```

- `VITE_API_URL=` (empty) is required: the Dockerfile defaults to
  `http://localhost:4000`, which would be baked into the bundle. Empty means
  same-origin; the VM's nginx serves the SPA and proxies `/api` and `/static`.
- `--platform linux/amd64` matches the e2 VMs.
- Tagging with the full `${REGISTRY}/...` name is what lets `docker push`
  know where to upload. `:${TAG}` (git SHA) is for rollbacks; the VM only
  pulls `:latest`.

Check they exist locally:

```bash
docker images | grep ${AR_REPO}
```

## 3. Log in to Artifact Registry

Only needed for pushing. With the service-account key, no gcloud needed:

```bash
cat ${GCP_KEY} | docker login -u _json_key --password-stdin https://${GCP_REGION}-docker.pkg.dev
```

The service account needs `roles/artifactregistry.writer` on the repo.

## 4. Push

```bash
docker push ${REGISTRY}/app:${TAG}
docker push ${REGISTRY}/app:latest

docker push ${REGISTRY}/frontend:${TAG}
docker push ${REGISTRY}/frontend:latest
```

### Push errors

| Error                                   | Cause                                                        |
|-----------------------------------------|--------------------------------------------------------------|
| `name unknown` / `repository not found` | Repo doesn't exist yet: run terragrunt apply for that env.   |
| `denied: ... uploadArtifacts`           | Service account lacks `roles/artifactregistry.writer`.       |
| `unauthorized`                          | `docker login` didn't succeed; redo step 3.                  |

## 5. SSH into the VM

Port 22 only accepts Google's IAP range and the VM uses OS Login, so always
tunnel through IAP; gcloud creates and registers the SSH key itself.

```bash
CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE=${GCP_KEY} \
gcloud compute ssh marketplace-dev-vm \
  --zone ${GCP_ZONE} --project ${GCP_PROJECT} --tunnel-through-iap
```

Needs `roles/compute.osAdminLogin` (sudo) and `roles/iap.tunnelResourceAccessor`.

## 6. Roll out on the VM

Everything lives in `/opt/marketplace`; every docker command needs `sudo`.

```bash
cd /opt/marketplace
sudo docker compose pull app frontend
sudo docker compose run --rm -e FLASK_APP=app/__init__alembic.py app flask db upgrade
sudo docker compose up -d --remove-orphans
sudo docker compose ps          # app should become "healthy"
sudo docker image prune -f
```

This is what `.github/scripts/deploy_vm.sh` runs in CI.

### Database migrations

Migration files ship inside the `app` image, so a new migration needs a
rebuild + push before `upgrade` sees it.

`deploy/vm/migrate.sh` wraps the commands below. Copy it to the VM once (and
again whenever it changes):

```bash
CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE=${GCP_KEY} \
gcloud compute scp deploy/vm/migrate.sh marketplace-dev-vm:/tmp/migrate.sh \
  --zone ${GCP_ZONE} --project ${GCP_PROJECT} --tunnel-through-iap
# then, on the VM:
sudo install -m 0755 /tmp/migrate.sh /opt/marketplace/migrate.sh
```

On the VM:

```bash
/opt/marketplace/migrate.sh            # flask db upgrade
/opt/marketplace/migrate.sh --pull     # pull the latest app image first
/opt/marketplace/migrate.sh current    # any other `flask db` command
```

The raw equivalents:

```bash
sudo docker compose run --rm -e FLASK_APP=app/__init__alembic.py app flask db current
sudo docker compose run --rm -e FLASK_APP=app/__init__alembic.py app flask db heads
```

### Changing environment variables

Edit `/opt/marketplace/app.env`, then recreate the container (`restart` keeps
the old environment):

```bash
sudo docker compose up -d --force-recreate app
sudo docker compose exec app env | grep REGISTRATION   # verify
```

## Generating a migration locally

```bash
docker compose -f docker-compose.local.yml up -d db

export FLASK_APP=app/__init__alembic.py
export DATABASE_URL=postgresql+psycopg2://marketplace:marketplace@localhost:5432/marketplace

flask db upgrade                       # bring the local DB to head first
flask db migrate -m "describe change"  # autogenerate
flask db upgrade                       # apply locally to verify
```

Review the file in `migrations/versions/` before committing, then rebuild and
push the `app` image (steps 2–4).

## Rollback

Re-point `:latest` at a previous SHA and roll out again:

```bash
docker pull ${REGISTRY}/app:<old-sha>
docker tag ${REGISTRY}/app:<old-sha> ${REGISTRY}/app:latest
docker push ${REGISTRY}/app:latest
```

Then run step 6 on the VM. Migrations are not rolled back automatically.

## Running the tests locally

The suite needs Postgres (listing search uses `pg_trgm`/`unaccent`) and uses
its own `marketplace_test` database, which it wipes after every test.

```bash
docker compose -f docker-compose.local.yml up -d db
# Only if your db volume predates docker/postgres/init:
docker compose -f docker-compose.local.yml exec db createdb -U marketplace marketplace_test

pytest -q        # add -p no:asyncio if pytest-asyncio is installed and clashes
```

Point `TEST_DATABASE_URL` elsewhere to use another database; never at real data.
