This is a demo app I built using Flask to learn how to create web apps in Python. It is a marketplace app for buying and selling things online. It features user accounts, listing items for sale, messaging users, and more.

Play around with demo at https://marketplace-app-flask.herokuapp.com/

### Screenshots
Browse all listings
![listings page](screenshots/screenshots1.png)
View listing details
![listing page](screenshots/screenshots3.png)
User profile page
![profile page](screenshots/screenshots2.png)

## Development

The app is a factory-built Flask app (`app.create_app`) configured per
environment (`development` / `testing` / `production`) via `APP_ENV`. Routes
are split into two blueprint layers: `app/routes/operations` holds the
actual business logic as JWT-protected, documented JSON endpoints under
`/api/v1/...` (Swagger UI at `/api/v1/docs/ui`); `app/routes/views` renders
the server-side HTML pages and calls straight into that logic layer
in-process instead of duplicating it.

```bash
cp .env.example .env            # fill in real secrets
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

docker compose up -d db redis   # or point DATABASE_URL/REDIS_URL elsewhere
flask db upgrade                # once a baseline migration exists, see below
flask run

pytest                          # runs against sqlite, no infra required
```

Postgres is the only supported database; Redis is wired up end-to-end
(config, client, docker-compose service) even though nothing uses it yet —
it's there for future caching/rate-limiting/vector-search work.

Since this refactor changed the schema (new `timestamp` /
`updated_timestamp` / `external_data` columns from `CRUDMixin`, Postgres
instead of SQLite), the existing files under `migrations/versions/` predate
it and are not a valid upgrade path. Generate a fresh baseline against a
running Postgres instance before deploying:

```bash
flask db migrate -m "baseline postgres schema"
flask db upgrade
```

### Running the full local stack

`docker compose up` brings up the app behind nginx, Postgres, Redis, and a
small observability stack (cadvisor + a StatsD exporter + Prometheus +
Grafana at `:3000`) mirroring the systemd + nginx setup under `deploy/`
used in production.

