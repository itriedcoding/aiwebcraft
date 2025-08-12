# Architecture

This project is a pnpm + Turbo monorepo that ships a Next.js App Router web app, a set of shared packages, and infra for Postgres (pgvector) and Redis.

## Components

- apps/web: Next.js app with API routes, rate limiting middleware, security headers, robots/sitemap
- packages/ai: Provider-agnostic text generation wrapper
- packages/codegen: Prompt → TSX component generator
- packages/agents: Agent workflow primitive (steps, execute)
- packages/evals: Evaluation runner for quality metrics
- packages/ui: Shared UI primitives (Button)
- packages/db: Prisma schema + client helpers
- packages/logger: Pino-based logger singleton
- packages/cache: Redis client and simple rate limiter helper

## Data flow (generate)

1. Studio calls `POST /api/generate` with `{ prompt }`
2. API uses `@acme/codegen` to turn the prompt into TSX
3. If DB is configured, `@acme/db` stores the generation
4. Response returns `{ ok, code }`
5. UI shows code and renders a live preview in Sandpack

## Extending

- Add new providers in `packages/ai`
- Add agents/evals to introduce iterative refinement
- Extend Prisma schema in `packages/db/prisma/schema.prisma`
- Add more UI primitives in `packages/ui`
- Introduce queues around Redis for long-running tasks