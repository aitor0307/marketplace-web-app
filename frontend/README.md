# Marketplace frontend

React SPA that replaces the Flask Jinja views (`app/routes/views`, now
deprecated). It talks only to the JSON API in `app/routes/operations`
(`/api/v1/...`, Swagger UI at `/api/v1/docs/ui`).

React 18 + TypeScript + Vite + Chakra UI v2 + TanStack Query + Zustand +
react-router v6 + i18next (en/es) — same stack and layout as `frontend/guest-app`.

## Quick start

```bash
# terminal 1: the Flask API on :4000 (the "CEVA-MP" launch config does this)
flask run --port 4000

# terminal 2
cd frontend
cp .env.example .env
npm install
npm run dev          # http://localhost:5173
```

With `VITE_API_URL` empty, the app calls the API same-origin and the Vite dev
server proxies `/api` and `/static` (listing images) to `VITE_DEV_PROXY_TARGET`.

## Scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Vite dev server |
| `npm run build` | Typecheck + production build → `dist/` |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript project references check |
| `npm run format` | Prettier |

## Deployment

`Dockerfile` / `Dockerfile.ci` build a static nginx image (SPA fallback,
`/healthCheck`), the same way as guest-app. Two ways to reach the API:

- **Same origin** (recommended): serve the SPA at `/` and proxy `/api/` and
  `/static/` to gunicorn on the same host. Leave `VITE_API_URL` empty.
- **Separate origin**: build with `VITE_API_URL=https://api.example.com` and
  add the SPA's origin to the backend's `CORS_ORIGINS`.

Set the backend's `FRONTEND_URL` so message-notification emails link to SPA
profile pages and deprecated views advertise their SPA successor.

## Architecture

Feature-first under `src/features/*` (`auth`, `listings`, `favorites`,
`users`, `messages`), each with `api/` (calls go through
`services/apiClient` only), `hooks/` (React Query), `screens/`, `types/`.

- `services/apiClient.ts` — fetch wrapper: bearer token, JSON/multipart
  bodies, both backend error shapes (`{error}` and pydantic `{message: [...]}`
  → per-field form errors), one transparent token refresh on expiry.
- `services/authService.ts` — token storage façade (localStorage).
- `providers/AuthProvider.tsx` — restores the session via `GET /api/v1/auth/me`.
- `app/routes.tsx` — routes, auth guards, and redirects from the old Jinja
  URLs (`/listing/3` → `/listings/3`, …) so bookmarks and sent emails keep working.

## Jinja view → SPA route

| Deprecated view | SPA route |
|---|---|
| `/`, `/index` | `/` |
| `/login`, `/register` | `/login`, `/register` |
| `/new_listing` | `/listings/new` |
| `/listing/<id>` (+ delete, favorite) | `/listings/:id` |
| `/user/<id>` | `/users/:id` |
| `/edit_profile` | `/profile/edit` |
| `/message/<id>?listing_id=` | `/users/:id/message?listingId=` |
| `/logout` | client-side (JWTs are stateless) |

Not ported: the Google Maps distance / Leaflet location map on listing and
profile pages.
