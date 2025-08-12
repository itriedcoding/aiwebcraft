# ACME V0x

An open, developer-first alternative to v0.dev — agentic, code-quality driven, and production-ready.

## Why this exists

- **Full control of code**: Everything is real, readable code in a modern monorepo
- **Agentic workflows**: Multi-step plans (parse designs → plan → generate → eval → iterate)
- **Production-grade**: TypeScript, tests, infra, and CI-ready from day one
- **Composable**: Swap AI providers, plug in your own evals and UI kit

## Features

- **Studio**: Prompt-to-code flow at `/studio` that returns React TSX
- **API-first**: `/api/generate` produces TSX from a prompt
- **Shared packages**: `@acme/ai`, `@acme/codegen`, `@acme/agents`, `@acme/evals`, `@acme/ui`
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
  - `@acme/config`: Shared config deps
- Tooling: pnpm + Turbo + TypeScript + Tailwind

## Getting started

1) Prereqs: Node 18+, pnpm 9+ (Corepack recommended)
2) Copy envs and fill what you need:

```bash
cp .env.example .env
```

3) Start local infra (optional if you don’t need DB/Redis yet):

```bash
docker compose up -d
```

4) Install dependencies:

```bash
pnpm install
```

5) Run dev:

```bash
pnpm dev
```

Open `http://localhost:3000/studio` and try a prompt.

## Environment variables

Key variables (see `.env.example` for full list):
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

## Scripts

- `pnpm dev` – run all apps in dev (Turbo)
- `pnpm build` – build all apps/packages
- `pnpm lint` – run linters
- `pnpm typecheck` – TypeScript checks

Per-package scripts (examples):
- `apps/web`: `dev`, `build`, `start`
- `packages/ui`: `build`, `dev` (tsup)
- `packages/*`: `build`, `dev`

## Development workflow

- All code lives in the monorepo. Import shared packages via `@acme/*` aliases.
- Next.js is configured to transpile workspace packages for smooth dev.
- Tailwind scans `packages/ui/src` so shared components style correctly.
- The Studio uses `/api/generate` which calls `@acme/codegen`. If no AI key is configured, a placeholder component is returned.

## Roadmap (high-level)

- Visual renderer to live-preview generated TSX
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
