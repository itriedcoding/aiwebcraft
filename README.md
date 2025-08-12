# ACME V0x

An open, developer-first alternative to v0.dev — agentic, code-quality driven, and production-ready.

## Quick links

- Studio: `http://localhost:3000/studio`
- Health: `GET /api/health`
- DB status: `GET /api/db` (requires Postgres running and `DATABASE_URL` configured)

## Why this exists

- **Full control of code**: Everything is real, readable code in a modern monorepo
- **Agentic workflows**: Multi-step plans (parse designs → plan → generate → eval → iterate)
- **Production-grade**: TypeScript, tests, infra, and CI-ready from day one
- **Composable**: Swap AI providers, plug in your own evals and UI kit

## Features

- **Studio**: Prompt-to-code flow at `/studio` that returns React TSX
- **API-first**: `/api/generate` produces TSX from a prompt
- **Shared packages**: `@acme/ai`, `@acme/codegen`, `@acme/agents`, `@acme/evals`, `@acme/ui`, `@acme/db`
- **Infra**: Postgres (pgvector) + Redis via Docker
- **Fallback dev**: Works without keys using a local placeholder generator

## Architecture

- Apps: `apps/web` (Next.js App Router)
- Packages: `packages/*`
  - `@acme/ai`: AI provider clients + abstractions
  - `@acme/codegen`: Prompt/design → code generation
  - `@acme/agents`: Multi-step workflows
  - `@acme/evals`: Quality metrics and scoring
  - `@acme/ui`: Reusable components
  - `@acme/db`: Prisma schema + client wrapper
  - `@acme/config`: Shared config deps
- Tooling: pnpm + Turbo + TypeScript + Tailwind + Prisma

## Getting started

1) Prereqs: Node 18+, pnpm 9+ (Corepack recommended)
2) Copy envs and fill what you need:

```bash
cp .env.example .env
# or if your UI hides dotfiles
cp env.example .env
```

3) Start local infra (optional if you don’t need DB/Redis yet):

```bash
docker compose up -d
```

4) Install dependencies:

```bash
pnpm install
```

5) Generate Prisma client (if DB used):

```bash
pnpm db:generate
```

6) Run dev:

```bash
pnpm dev
```

Open `http://localhost:3000/studio` and try a prompt.

## Environment variables

Key variables (see `.env.example` and `env.example` for full list):
- **App**: `NEXT_PUBLIC_APP_URL`
- **Auth**: `NEXTAUTH_URL`, `NEXTAUTH_SECRET`
- **Database**: `DATABASE_URL`
- **Redis**: `REDIS_URL`
- **AI Providers**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`
- **Figma**: `FIGMA_PERSONAL_ACCESS_TOKEN`
- **GitHub**: `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- **Email**: `RESEND_API_KEY`, `SENDGRID_API_KEY`
- **Analytics**: `POSTHOG_API_KEY`, `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_POSTHOG_HOST`, `PLAUSIBLE_DOMAIN`, `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`
- **Monitoring**: `SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN`

This repo runs with no keys thanks to a local fallback for codegen. Add provider keys when you’re ready.

## REST API

- `POST /api/generate`
  - Body: `{ "prompt": string, "temperature"?: number }`
  - Response: `{ ok: boolean, code?: string, error?: string }`

- `GET /api/health`
  - Response: `{ ok: true, uptime: number }`

- `GET /api/db`
  - Response: `{ ok: boolean, projects?: number }`

## Database

- Edit schema: `packages/db/prisma/schema.prisma`
- Generate client: `pnpm db:generate`
- Create dev migration: `pnpm db:migrate`
- Open Prisma Studio: `pnpm db:studio`

## Scripts

- `pnpm dev` – run all apps in dev (Turbo)
- `pnpm build` – build all apps/packages
- `pnpm lint` – run linters
- `pnpm typecheck` – TypeScript checks
- `pnpm db:*` – Prisma helpers

## Development workflow

- All code lives in the monorepo. Import shared packages via `@acme/*` aliases.
- Next.js is configured to transpile workspace packages for smooth dev.
- Tailwind scans `packages/ui/src` so shared components style correctly.
- The Studio uses `/api/generate` which calls `@acme/codegen`. If no AI key is configured, a placeholder component is returned.

## Roadmap (high-level)

- Visual renderer to live-preview and mount generated TSX in a sandbox
- Figma ingestion: parse auto-layout and translate to components
- Agentic loops: plan → generate → test/eval → refine
- Project persistence with Postgres; job orchestration with Redis
- Export to GitHub and open PRs with CI templates
- One-click deploys (Vercel/Fly/Render)

## Deployment

- Create your `.env` with production URLs and keys
- Build: `pnpm build`
- Run web: `pnpm --filter @acme/web start`
- Or deploy the Next.js app to your platform of choice (e.g. Vercel)

## License

MIT — use freely, contributions welcome.
