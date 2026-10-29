---
name: hos-backend
description: Build a HumanifyOS back-end ticket the HOS way — add a process, route, event, table or config key in the right folder, with the right tests and commands.
---

# hos-backend

Use this when implementing any ticket in HumanifyOS (Go).

## Steps
1. Read `AGENTS.md`, then the ticket (`/HOSPACK/HOS/JIRA_IMPORT.json`, `externalId` = tempId) and every `/HOSPACK/HOS/...` link it names (spec pages, fixtures, OpenAPI).
2. Put code where the layout says: process → `apps/<module>/<name>`; module code → `internal/<module>/<pkg>`; shared by ≥ 2 modules → `pkg/lib/<lib>`; enums/errors/events/models → `pkg/common` (append only).
3. Contract first: OpenAPI change in `/HOSPACK/HOS/<MODULE>/spec/openapi` → `make codegen` → `pkg/contracts/<module>`; never edit generated files.
4. Events: `pkg/common/events.go` constant, one `pkg/lib/events/subscriptions.go` row per consumer app-id, `/events/<type>` handler, `make dapr-subs`, and the six-column row in the module's `spec/EVENTS.md`.
5. Data: migration file with the next free number, RLS through `txn`, `pkg/common/models` append, SCHEMA.md row; `make schema-test`.
6. Config: register in `pkg/lib/config`, document in CONFIG-KEYS.md; secrets only as `secretRefs`.
7. Tests: one Go test per acceptance criterion named `Test_<ID>_AC<n>`, fakes for vendors, stub tokens; `make test lint spec-lint arch-lint` green.
8. PR titled `[{TEMP_ID}] {summary}` with a `RESULT.json` body, one `- [{TEMP_ID}] <summary>` line appended under Unreleased in `CHANGELOG.md`, commit trailer `Ticket: {TEMP_ID}`. The `Test command:` AC must run green on the rebased head without another lane's process (stub PATH, recorded answers, the compose stores). Then stop: the orchestrator merges on green, moves Jira, and closes gates with `make gate-close` (P-11) — you never merge or touch Jira.

## Do not
- import another module's `internal`; call a service by URL; add a wildcard subscription; put a secret in git; read tenant ids from a request body; depend on the GOD token.
