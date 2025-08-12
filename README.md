# ACME V0x

An open, developer-first alternative to v0.dev — agentic, code-quality driven, and production-ready.

## Quick links

- Studio: `http://localhost:3000/studio`
- Health: `GET /api/health`
- DB status: `GET /api/db`

## Why this exists

- **Full control of code**: Everything is real, readable code in a modern monorepo
- **Agentic workflows**: Multi-step plans (parse designs → plan → generate → eval → iterate)
- **Production-grade**: TypeScript, tests, infra, and CI-ready from day one
- **Composable**: Swap AI providers, plug in your own evals and UI kit

## Features

- **Studio**: Prompt-to-code flow at `/studio` that returns React TSX (no-key fallback included)
- **API-first**: `/api/generate` produces TSX from a prompt
- **Security**: Sensible headers, middleware-based rate limiting
- **Observability**: `@acme/logger` (pino)
- **Infra**: Postgres (pgvector) + Redis via Docker
- **Packages**: `@acme/ai`, `@acme/codegen`, `@acme/agents`, `@acme/evals`, `@acme/ui`, `@acme/db`, `@acme/logger`, `@acme/cache`

## Architecture (high-level)

```
+------------------+      +-------------------+      +------------------+
| apps/web (Next)  | ---> |  /api/* routes    | ---> |  packages/*      |
|  UI + middleware |      |  generate/health  |      |  ai/evals/agents |
+------------------+      +-------------------+      |  codegen/ui/db   |
        |                                                +--------------+
        v                                                |  cache/log   |
+------------------+                                     +--------------+
|  Browser / Studio|                                     Postgres/Redis
+------------------+
```

## Getting started

1) Prereqs: Node 18+, pnpm 9+ (Corepack recommended)
2) Copy envs and fill what you need:

```bash
cp .env.example .env
# or if your UI hides dotfiles
cp env.example .env
```

3) Start local infra (optional):

```bash
docker compose up -d
```

4) Install deps:

```bash
pnpm install
```

5) (DB) Generate Prisma client:

```bash
pnpm db:generate
```

6) Dev:

```bash
pnpm dev
```

Open `http://localhost:3000/studio`.

## Environment variables

See `.env.example` and `env.example`. Minimal setup to start: none required (uses fallback generator). For DB/Redis and providers, set the corresponding keys.

## REST API

- `POST /api/generate` → returns TSX from a prompt
- `GET /api/health` → simple uptime
- `GET /api/db` → DB connectivity check

## Rate limiting

- Implemented via middleware (`apps/web/middleware.ts`) using `@acme/cache` (Redis).
- Defaults: 20 req / 10s per IP+path. Configure via environment (add your own logic).

## Security & Compliance

- Headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`
- Secrets: `.env` files, not committed
- Error monitoring hooks present (Sentry keys in example)
- Analytics optional (PostHog/Plausible)

## Performance

- Next.js app router, package transpilation for fast local DX
- Tailwind purges across app + shared UI
- Turbo caches builds & outputs

## Database

- Schema: `packages/db/prisma/schema.prisma`
- Migrate (dev): `pnpm db:migrate`
- Studio: `pnpm db:studio`

## Build & Deploy

- Docker:

```bash
docker build -t acme-v0x .
docker run --env-file .env -p 3000:3000 acme-v0x
```

- Vercel: import the repo, set environment variables, and build. Next.js app is in `apps/web`.

## CI

- GitHub Actions workflow installs deps, typechecks, and builds on PRs/commits to `main`.

## Scripts

- `pnpm dev` – run all apps in dev (Turbo)
- `pnpm build` – build all apps/packages
- `pnpm typecheck` – TypeScript checks
- `pnpm db:*` – Prisma helpers

## Roadmap (selected)

- Live sandbox preview to mount generated TSX
- Figma ingestion + layout synthesis
- Agentic loops with evals and retries
- Project persistence and long-running jobs
- GitHub export with CI templates
- One-click deploys (Vercel/Fly/Render)

## License

MIT.
