# Install dependencies
FROM node:20-alpine AS deps
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml turbo.json .npmrc* ./
COPY apps ./apps
COPY packages ./packages
RUN npm i -g pnpm@9.6.0 && pnpm install --frozen-lockfile=false

# Build
FROM node:20-alpine AS builder
RUN corepack enable
WORKDIR /app
COPY --from=deps /app /app
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/apps/web/.next /app/apps/web/.next
COPY --from=builder /app/apps/web/package.json /app/apps/web/package.json
COPY --from=builder /app/node_modules /app/node_modules

EXPOSE 3000
CMD ["pnpm", "--filter", "@acme/web", "start"]