---
name: hos-frontend
description: Build a HumanifyOS-UI ticket the HOS way — add a route, module, query hook, contract or ui component in the right package, with the right tests and commands.
---

# hos-frontend

Use this when implementing any ticket in HumanifyOS-UI (Workbench, Quality, shared packages).

## Steps
1. Read `AGENTS.md`, then the ticket (`/HOSPACK/HOS/JIRA_IMPORT.json`, `externalId` = tempId) and the mock on its first line.
2. Regenerate contracts if the OpenAPI changed: `pnpm codegen` (→ `packages/contracts/<module>`). Never edit generated files; a refinement the spec cannot express (`.refine()`, `.transform()`, branded ids) goes in `packages/contracts/<module>/refine.ts`, wrapping the generated schema, exported through the same subpath.
3. Put code where the layout says:
   - a screen → `apps/web/<app>/src/modules/<feature>/components/*` + `model/*`; expose it from a thin file in `src/routes/`
   - data access → `src/api/<resource>.ts` (or `packages/api/<resource>.ts` when two apps need it): TanStack Query keys `['<resource>', …]`, mutations invalidate by resource
   - shared visuals → `packages/ui/src/<area>` (vendored shadcn/Base UI; tokens only from the Tailwind preset)
   - cross-app screens → `packages/features/<name>`
   - http/auth/telemetry → `packages/platform/<area>` only
4. State: URL for filters/tabs/pagination/selection (typed search params); Query for server data; Zustand (factory) for feature UI state.
5. Tests: one Vitest test per acceptance criterion, named after it (`AC-1 …`), MSW handlers from `packages/testing`; axe on new screens.
6. Run `pnpm typecheck && pnpm lint && pnpm test`; fix boundary lint errors by moving code, not by disabling the rule.
7. Open the PR titled `[{TEMP_ID}] {summary}` with a `RESULT.json` body, one `- [{TEMP_ID}] <summary>` line appended under Unreleased in `CHANGELOG.md`, commit trailer `Ticket: {TEMP_ID}`. The `Test command:` AC runs green on the rebased head with msw fixtures alone (a live BFF or platform is a gate check). Then stop: the orchestrator merges on green, moves Jira, and closes gates with `make gate-close` (P-11) — you never merge or touch Jira.

## Do not
- import another app's modules; copy a `packages/ui` component; call `fetch` outside `packages/platform/http`; render a literal `-1`; hard-code a channel list.
