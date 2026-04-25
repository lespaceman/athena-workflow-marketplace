---
name: tanstack-start-guide
description: >
  Use when building, modifying, scaffolding, or debugging TanStack Start applications. Triggers
  include "TanStack Start", "React Start", "start-basic", "file-based routes", "authenticated
  routes", "deferred data", "tRPC with TanStack Start", "React Query with TanStack Start",
  "location masking", "navigation blocking", "view transitions", or requests to choose or adapt a
  TanStack Start example scaffold.
---

# TanStack Start Guide

## What this skill is for

Use this skill to orient full-stack React work around TanStack Start conventions: file-based
routing, server functions, loaders, route-level data, app scaffolds, and integration examples.

This skill is the marketplace entry point. Upstream Agent Skills fetched with `@tanstack/intent`
are copied under `skills/upstream/@tanstack/`; load the most specific upstream skill before making
framework-specific changes.

## Upstream skills copied from `@tanstack/intent`

The upstream install reported 6 intent-enabled packages and 22 skills:

| Package | Skills |
|---|---|
| `@tanstack/react-start` | `react-start`, `react-start/server-components`, `lifecycle/migrate-from-nextjs` |
| `@tanstack/router-core` | `router-core`, `router-core/auth-and-guards`, `router-core/code-splitting`, `router-core/data-loading`, `router-core/navigation`, `router-core/not-found-and-errors`, `router-core/path-params`, `router-core/search-params`, `router-core/ssr`, `router-core/type-safety` |
| `@tanstack/router-plugin` | `router-plugin` |
| `@tanstack/start-client-core` | `start-core`, `start-core/deployment`, `start-core/execution-model`, `start-core/middleware`, `start-core/server-functions`, `start-core/server-routes` |
| `@tanstack/start-server-core` | `start-server-core` |
| `@tanstack/virtual-file-routes` | `virtual-file-routes` |

Copied source root:

```text
plugins/tanstack-start/skills/upstream/@tanstack/
```

## Example scaffolds

Known TanStack Start example families include:

- Basic (`start-basic`)
- Basic + Auth (`start-basic-auth`)
- Counter (`start-counter`)
- Basic + React Query (`start-basic-react-query`)
- Clerk Auth (`start-clerk-basic`)
- Convex + Trellaux (`start-convex-trellaux`)
- Supabase (`start-supabase-basic`)
- Trellaux (`start-trellaux`)
- WorkOS (`start-workos`)
- Material UI (`start-material-ui`)

Known file-based router examples include:

- Quickstart
- Basic
- Kitchen Sink
- Kitchen Sink + React Query
- Location Masking
- Authenticated Routes
- Scroll Restoration
- Deferred Data
- Navigation Blocking
- View Transitions
- With tRPC
- With tRPC + React Query

## Workflow

### 1. Identify the target scaffold

Choose the closest existing example before writing new structure:

| Need | Prefer |
|---|---|
| Minimal app shell | `start-basic` or file-based Basic |
| Authenticated app routes | `start-basic-auth`, Authenticated Routes, Clerk, Supabase, or WorkOS |
| Client/server data caching | `start-basic-react-query` or Kitchen Sink + React Query |
| API contract layer | With tRPC or With tRPC + React Query |
| Route UX behavior | Location Masking, Scroll Restoration, Navigation Blocking, or View Transitions |
| Product-style CRUD board | Trellaux or Convex + Trellaux |
| Design-system integration | Material UI |

### 2. Inspect the project before editing

- Find the package manager and scripts.
- Read the current route tree, app entrypoints, and server/runtime configuration.
- Check whether TanStack Router, TanStack Start, React Query, auth, database, or RPC integrations
  are already present.
- Prefer the project's current conventions over reshaping it to match an example exactly.

### 3. Implement in framework-shaped increments

- Keep route files colocated with their route behavior.
- Use semantic route boundaries instead of large catch-all components.
- Put server-only work in the server-side surfaces expected by the project.
- Keep loaders and data dependencies close to the routes that consume them.
- Add React Query, tRPC, auth, or persistence only when the requested feature needs it.

### 4. Validate

Run the most relevant project commands after changes, usually in this order:

1. Typecheck or lint
2. Unit/component tests when present
3. Build
4. Targeted browser or E2E checks for user-facing route behavior

If a validation command is unavailable or blocked by missing environment variables, record the exact
blocker.

## Guardrails

- Do not assume one example scaffold is canonical for every app.
- Do not add auth, RPC, database, or React Query layers unless the user request or existing app
  architecture calls for them.
- Do not overwrite existing routing structure without first understanding it.
- Do not invent package-specific API details when upstream TanStack docs or installed examples are
  available locally.
