FROM node:24-slim AS base

# Recent Node images don't reliably ship Corepack enabled by default, so pin
# and install pnpm directly rather than depending on `corepack enable`.
RUN npm install -g pnpm@12.4.2
WORKDIR /app

FROM base AS dev

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .

EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]

# Produces a static build at /app/build. Not a runnable service on its own:
# Caddy serves the output directly. See caddy/Dockerfile.production.
FROM base AS static-build

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build
