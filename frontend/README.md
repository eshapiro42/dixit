# Dixit frontend

A SvelteKit static SPA. Talks to the backend over `/api/*` and a Socket.IO connection at `/socket.io`, both same-origin in production behind Caddy.

## Developing

```sh
pnpm install
pnpm dev
```

The dev server proxies `/api` and `/socket.io` to `http://127.0.0.1:8000`, so run the backend locally alongside it (see `../backend/README.md`).

## Checks

```sh
pnpm check       # svelte-check
pnpm lint        # prettier + eslint
pnpm test:unit   # vitest (node + browser component tests)
pnpm test:e2e    # playwright
```

## Building

```sh
pnpm build
```

Outputs a static site to `build/`.
