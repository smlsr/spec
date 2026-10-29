# Back-end platform architecture — HumanifyOS

One Go module (`bitbucket.org/ttec/humanifyos`, Go 1.23), many processes, four platform modules (LOOM, SWATCH, RUBRIC, CORE) plus the end-user application module APP, owned by the sibling program HOS-UI (`HOS-UI/` pack; `apps/app`, `internal/app`, `pkg/contracts/app` are HOS-UI's folders), on one
Postgres `txn` spine, one Dapr bus (`loom-bus`, NATS JetStream) and Dapr service invocation between processes. This page is the canonical
text; `AGENTS.md` is the one-page version every agent reads; `.golangci.yml` + `tools/arch-lint.sh` enforce the dependency rules.

## 1. Repository structure

```
HumanifyOS/
  VERSION  go.mod  Makefile  bitbucket-pipelines.yml
  apps/
    loom/<process>/        ingest-gw, item-api, spine-writer, interrogator/{pass1,pass2,ready}, linker, identity, star-projector, chunker,
                           embed-worker, embed-api, index-writer, rerank-gateway, vertical-registry, metric-registry, annotate-api,
                           query-plane/{core,legs/*,combine,explain,nl}, dataset-svc/{crud,lifecycle,derive}, export-svc, evidence-api,
                           qa-api/{bundles,calibrations,coaching,registry}, eval-runner, taxonomist, graph-projector, graph-api, watchers/{api,detectors},
                           replay-controller, retention-gc, dataset-gc, bus-dlq, seed-loader/{steps}, _hello
    swatch/swatch-gw/{session,compile,rows,render,obs}
    rubric/{rubric-maint, rubric-scheduler}
    core/{core-api, litecard-engine, rubric-engine, fact-engine, score-engine, cares-engine, qa-orchestrator, hos-token}
    app/{hos-appserver/server, hos-ws, hos-seed/steps}      — owned by the HOS-UI program (HOS-UI/APP pack); HOS never imports it
  internal/
    loom/<pkg>/            module-private LOOM code (project-private packages that used to sit under cmd/<project>)
    rubric/<pkg>/          RUBRIC domain code (validate, lifecycle, assign, score, dryrun, channels, clients …)
    core/<pkg>/            CORE domain code (org, auth, sso, models, cares, engines, fixtures …)
    app/<pkg>/             APP domain code (persona, resolvers, adapters, clients, rules, cache, events, ws, stub, registry …) — owned by the HOS-UI program
  pkg/
    lib/<lib>/             platform libraries used by two or more modules: token, auth, events (codec, Publisher, subscriptions.go), bus,
                           invoke, obs, log, config, httpx, httpserver, tenancy, dbx, objstore, llm, embed, dlp, packfiles, packs, graph,
                           archive, media, er, gaps, facts, cqltypes, catalog, money, resolver, recipes, jsonschema, cite, stars, graphio,
                           channels, itemmeta, enginekit, util
    common/                enums, error codes (errors.go), event type constants (events.go), models/ — append-only files
    contracts/<module>/    openapi.yaml (copy of /HOSPACK/HOS/<MODULE>/spec/openapi) + generated types (oapi-codegen) — never hand-edited
  migrations/              0001…0025 from /HOSPACK/HOS/*/spec/sql — only M-*/R-01/C-01/M-2x tickets edit; lock unit = one file
  deploy/                  compose.yml, dapr/ (components, subscriptions/<app-id>.yaml), helm/<process>, terraform/, datadog/, otel/
  scripts/                 install-*.sh seed-dev.sh seed-org.sh doctor.sh backup-verify.sh …
  fixtures/                copy of /HOSPACK/HOS/*/spec/fixtures (never edited here)
  tools/                   spec_lint.py, helm-matrix.sh, arch-lint.sh, codegen — CI only
  test/{e2e,golden,perf}
  docs/{adr,runbooks}
```

## 2. Dependency rules (imports flow downward only)

```
apps/<module>/*      →  internal/<module>/*, pkg/lib/*, pkg/common, pkg/contracts/<module>
internal/<module>/*  →  internal/<module>/*, pkg/lib/*, pkg/common, pkg/contracts/*     (never another module's internal)
pkg/lib/*            →  pkg/lib/*, pkg/common                                          (pkg/lib/httpserver is the one wiring point)
pkg/common           →  nothing internal
pkg/contracts        →  nothing internal
```

Cross-module behaviour never crosses an import boundary: it goes through Dapr service invocation (`pkg/lib/invoke`, Bearer forwarded) and the
bus (`pkg/lib/events.Publisher`, CloudEvents with `loomtenant/loomprogram/loomsubtenant/loomtxn`). `apps/*/main.go` only wires
config → log → obs → db → bus → router; business code lives in the lock-unit sub-folders. No `nats.Connect`, no `http.Get("http://<service>:port")`.

## 3. Conventions that every process shares

- Bearer auth via `pkg/lib/token.UnpackToken` (stub tokens under `LOOM_TOKEN_STUB=1`, refused outside dev/ci); three-level scope tid/pid/sid;
  revocation through the `hos-revocations` state store; the GOD-token bridge is fenced `GOD-TOKEN(Q-31)` and removed by C-70.
- One `Problem` error shape, `bearer` security scheme, every ingress pattern `/v1/<area>/**`, one area per gateway.
- Events: one explicit subscription per type (rows in `pkg/lib/events/subscriptions.go`, rendered to `deploy/dapr/subscriptions/<app-id>.yaml`
  by `make dapr-subs`), handlers at `/events/<type>`, idempotent consumers, DLQ after the bus's retries; never a wildcard subscription.
- Tenancy: every scoped row hangs off `txn` (RLS `txn_iso`); tenants/programs/LOBs are created only by core-api; sentinel `*`.
- Config keys are registered (`pkg/lib/config`), documented in `/HOSPACK/HOS/<MODULE>/spec/CONFIG-KEYS.md`, no secret values in git.
- Tests are named after acceptance criteria (`Test_<ID>_AC1`), run with fakes for vendors and stub tokens; the compose e2e gate (P-10; HOS-UI's X-06 for the app) is where
  the real stack meets.

## 4. Adding things the HOS way

| You want to add… | Where it goes | What else changes |
|---|---|---|
| a process | `apps/<module>/<name>/main.go` + sub-folders | `deploy/dapr/apps.yaml` row (port, `routes_prefix`), Helm chart, PROCESSES.md in the pack |
| a route | the gateway's sub-folder; contract first in `/HOSPACK/HOS/<MODULE>/spec/openapi` → `pkg/contracts/<module>` regenerated | AUTH-TENANCY route→scope row |
| an event | constant in `pkg/common/events.go`, row in `pkg/lib/events/subscriptions.go` per consumer, `/events/<type>` handler | `/HOSPACK/HOS/<MODULE>/spec/EVENTS.md` six-column row (the program catalog is generated from it) |
| a table/column | migration file (next free number in `/HOSPACK/HOS/schema/MIGRATIONS.md`) + `pkg/common/models` append | SCHEMA.md row; RLS through `txn` |
| a config key | `pkg/lib/config` registration | CONFIG-KEYS.md row |
| shared code | `pkg/lib/<lib>` when two modules need it; else `internal/<module>/<pkg>` | never `internal/<other module>` |
