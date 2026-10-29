# Front-end platform architecture — HumanifyOS-UI

A shared React and TypeScript foundation for several web applications (and, when one appears, Chrome extensions). 3–5 developers, greenfield, two surfaces. This page is the canonical text of `docs/frontend-platform-architecture.html`; the dependency rules below are enforced by `tooling/eslint/boundaries.js` and by package manifests.

Imports flow downward only:

```
web apps · extensions
        ↓
     features            screens, components shared by more than one app
      ↓      ↓
     ui     api          ui: tokens, primitives, patterns, forms · api: queries, mutations, keys
      ↓      ↓
  platform  contracts    platform: http, auth, telemetry, flags, result, utils · contracts: Zod schemas, the API boundary
```

## 1. The stack

| Concern | Choice | Why |
|---|---|---|
| Repository | pnpm workspaces + Turborepo | Cached task execution with minimal configuration. Strict resolution rules out phantom dependencies across shared packages. |
| Web apps | Vite + React 19 + TanStack Router, SPA | Authenticated internal apps have no server-rendering need, so no per-app server runtime. Routes and search params are typed end to end. |
| Compiler | React Compiler, on by default | Automatic memoization at build time; manual `useMemo`/`useCallback` only where profiling shows a need. |
| Extensions | WXT + React | Manifest generation, file-based entrypoints, hot reload in every context, shadow-root mounting for content scripts. Chrome extensions are planned for the release after this one (Q-45): `packages/platform/http` and `auth` are built extension-safe now (injected fetch + token provider, core + adapters), `apps/extensions/` stays reserved. |
| Server state | TanStack Query | Caching, revalidation and deduplication. Queries, keys and invalidation are organised by API resource, not by feature. |
| URL state | TanStack Router search params | Filters, tabs, pagination and selection live in the URL: typed, validated, shareable. |
| Client state | Zustand, feature-scoped | Small and unopinionated. Stores come from factories, never module singletons. |
| Forms | TanStack Form + Zod | Same family as router and query. |
| Contracts | Zod schemas **generated from the HOS OpenAPI files**, refined beside them | Parsed at the HTTP boundary. `/HOSPACK/HOS/<MODULE>/spec/openapi/*.yaml` are the source; `pnpm codegen` regenerates `packages/contracts/<module>`; consumers never change when the generator does. What the spec cannot express (`.refine()`, `.transform()`, branded ids, cross-field rules) lives in `packages/contracts/<module>/refine.ts`, wrapping the generated schema and exported through the same subpath — never a parallel hand-written schema (Q-42). |
| UI | Vendored shadcn on Base UI, tokens, Tailwind v4 preset | Base UI is shadcn's default primitive layer. Components are owned once vendored; updates are reviewed. Apps consume the package, never their own copies. |
| Testing | Vitest, Testing Library, MSW, Playwright | Mocks validate against the same contract schemas as the client. MSW serves unit tests; `services/mock-api` serves local development and end-to-end runs. Playwright runs only in the live-smoke slots (P-10, RU-24, CU-22; HOS-UI's X-10 for the Quality app). |
| Telemetry | OpenTelemetry behind an internal wrapper | One interface for traces, errors and events. Vendor SDKs never imported outside it. |
| Versions | pnpm catalogs | Each third-party version declared once. |

## 2. Repository structure

```
apps/
  web/
    workbench/        LOOM Workbench (+ SWATCH /swatch, RUBRIC /rubrics, CORE /control areas)  — Vite + TanStack Router SPA
    quality/          TTEC Quality (APP personas: agent, supervisor, ops leader, VoC) — owned by the HOS-UI program (HOS-UI/APP pack), as are packages/ui/src/quality, packages/contracts/app, packages/testing/src/app and the app fixtures of services/mock-api
  extensions/         (none yet; WXT when one appears)
packages/
  api/                queries, mutations, keys shared by more than one app, by resource
  features/           screens and components shared by more than one app
  ui/                 tokens, primitives, patterns, forms (vendored shadcn on Base UI, Tailwind v4 preset)
  contracts/          Zod schemas generated from the HOS OpenAPI files — one folder per module (loom, swatch, rubric, core, app)
  platform/           http, auth, extension, telemetry, flags, result, utils
  testing/            MSW handlers, fixtures (mirrors /HOSPACK/HOS/*/spec/fixtures)
  rubric-score/       pure scoring library (RUBRIC) · cares-score/ pure CARES maths (CORE)
services/
  mock-api/           local API for development and tests (serves the HOS fixtures)
tooling/              tsconfig, eslint (boundaries), tailwind preset, vite preset
```

Apps are grouped by surface because build tooling, release cadence and CI differ. Subfolders become separate packages only when a boundary needs enforcing.

## 3. Inside an application

```
apps/web/workbench/src/
  routes/             file-based route tree, thin
  api/
    items.ts          queries, mutations, keys — one file per resource, mirrors packages/contracts
    datasets.ts
  modules/            features: screens, components, UI state
    query/
      components/
      model/          types, mapping, logic
  app/                providers, router, error boundaries
  lib/                app-local instances (session, API client) and helpers
```

Modules are owned by the app and may import one another freely; routes stay thin and compose them. `api/` mirrors `contracts/`, one file per resource. Anything a second app needs moves to `packages/api` or `packages/features`, with app-specific parts injected by the host.

## 4. Dependency rules

```
app        →  features, api, ui, contracts, platform
features   →  api, ui, contracts, platform
api        →  contracts, platform
ui         →  platform                 (tokens and utilities only)
contracts  →  platform                 (result and utils only)
platform   →  nothing internal
```

Rules are checked twice: on package manifests, and by lint rules on imports (`tooling/eslint/boundaries.js`). A `ui` component may not know about contracts, transport or auth. Packages expose subpath exports rather than one barrel, keeping builds incremental and tree-shaking honest.

## 5. Extension constraints (when an extension exists)

Transport-agnostic HTTP client (`fetch` and the token provider are injected); auth as core plus adapters (refresh/expiry shared, token storage per surface); shadow-root-safe UI (portals attach to the shadow root, not `document.body`); the service worker is the trust boundary; the API tolerates older extension clients.

## 6. State model

| Kind | Owner | Shape |
|---|---|---|
| Server state | TanStack Query | Most of what gets called state. Apps reading the same resource cache it independently; keys and the fetch layer are standardised, not a runtime. Caches are per user and cleared on logout. |
| Session | Auth layer (`packages/platform/auth`) | HOS Bearer tokens (`UnpackToken` semantics, three-level scope tid/pid/sid) are the core; the IdP adapter is CORE's SSO. Token scope is displayed, never widened by the UI. |
| Client UI state | Zustand | Per app, per feature. Sharing it across deployed apps would couple their releases. |

Anything the URL can own lives in search params. Nothing Query owns belongs in Zustand, and nothing the URL should own belongs in either.

## 7. HOS specifics

- Every screen is a UI ticket in `/HOSPACK/HOS/JIRA_IMPORT.json`; its first line names the mock (`/HOSPACK/HOS/<MODULE>/ui/…`). Build to the mock; the shots are the visual baseline.
- Errors are the one `Problem` shape `{error, code, message, pointer?, details?}`; `packages/platform/http` maps 401 → token screen, 403 → "Not permitted", 404 → "Not in your scope", 429 → countdown.
- Stub values from HOSAppServer (`X-HOS-Stub`) render the `Unavailable` atom, never `-1`.
- Channels come from `GET /v1/registry/channels` (never an enum); metadata is read from `GET /v1/items/{id}/metadata`.

Open: internationalisation approach and tooling. Shared `ui` components already take all user-facing text as props.

Revisit when cached CI runs pass fifteen minutes, the package count passes twenty-five, or a second team joins the repository.
