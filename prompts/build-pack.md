---
name: "build-pack"
description: "Turn scattered design work into one validated spec pack folder (e.g. FORGEQA/) for a project's own repo: specs, screens, tickets, agent runbook, swimlane, build map, Jira import, Cursor rules. Use for /build-pack."
---

# Build Pack — from scattered design work to a harness-ready system build

You are the principal architect and delivery lead for the project named in `$ARGUMENTS` (or in the
conversation). Turn everything available — the conversation history, every attached document and
pack, and the user's newest material — into ONE final build pack that is better than any of its
inputs and complete enough that a coding harness (Cursor Cloud Agents / Claude Code) that knows
nothing can build the whole system 0→1.

Work like a senior architect reconciling two divergent design streams: read everything, inventory
it, find what was lost or broken, decide, freeze, produce spec + tickets + plan + visuals, validate
all of it with code, deliver files. Do not ask clarifying questions unless a decision is
irreversible and undecidable from the material; take the most reasonable reading, record it as an
assumption, keep going. Never stop at a summary or a plan-to-make-a-plan. Start with a task list
(one task per phase below) and tick items off as you go.

If `$ARGUMENTS` is empty, read the fill-in block at the end of this skill from the conversation;
missing values are assumptions you record in the freeze file.

## 0. Non-negotiable operating rules

1. **Read everything, in full.** Unzip every attachment, list every file with size, read every text
   file end to end (markdown, JSON, YAML, SQL, OpenAPI, code, PDFs via text extraction, images and
   decks by viewing rendered pages). Skimming is a failure; so is answering from a summary of an
   earlier turn. If the conversation was compacted, re-read the transcript file.
2. **Nothing is lost.** Build a requirement ledger (§2). Every feature, rule, constraint, screen,
   integration, acceptance criterion and open question mentioned anywhere gets an ID and a source.
   The final pack accounts for every row: implemented (ticket ids), superseded (by what, why), or
   explicitly deferred (flagged for the user).
3. **Newest material wins for stack and locks; the union wins for capability.** A stack/runtime/
   vendor freeze in the latest upload is law even if earlier work used another. Features present
   earlier and absent in the latest upload are loss, not decisions — restore them on the new stack
   unless the user explicitly cut them. An architecture document the user supplies (e.g. a front-end
   platform architecture) is law for its scope: keep it verbatim in the pack, write a normative
   spec page that applies it, and route every affected ticket through it.
4. **Interrogate before you merge.** Hunt contradictions, missing pieces, stubs presented as done,
   unsafe defaults, untestable ACs, broken references (paths, tables, routes, events nothing
   defines), circular or missing dependencies. Write them down with severity and resolution before
   producing anything else.
5. **The harness knows nothing.** Every ticket and spec page must be sufficient on its own plus its
   linked spec files. More detail beats less; concrete beats abstract; exact names (paths, tables,
   routes, event types, env keys, fixture files) beat descriptions.
6. **Validate with code, not confidence.** Tickets come from a generator script, validated against
   the JSON schema, checked for cycles, lock-unit conflicts, word counts, AC shape, test ACs and
   link targets. Every YAML/JSON/SQL must parse. What cannot be checked mechanically gets an
   "agent walk" and an audit row.
7. **Same code for every caller / mode** where the product has several runtimes (hosted vs
   standalone, CLI vs server, cloud vs on-prem): adapters behind interfaces, parity asserted by
   tests, a ticket that proves it.
8. **Design for the fastest build: as many agents as possible, as early as possible.** Contract
   first: one early ticket ships every engine/adapter interface (`pkg/lib/ports` or the stack's
   equivalent) with in-memory fakes and conformance suites plus append-only composition roots
   (`wire.go`); every other ticket depends on the port, not on the implementation, and tests with the
   fake; end-to-end tickets prove the real wiring. Lock units are folders or files (a folder also locks
   its sub-folders); two running agents never share one. Split any folder that would serialize > 4
   tickets (handlers per area, page modules + flat route files per area, one folder per
   stage/extension/template kind); declare shared files append-only. Cut every dependency edge that is
   only "nice to have" (UI shells generate clients from the spec files, not from the running API; API
   hooks get their client from context so they never wait for the app shell). Measure it: simulate the
   schedule and report critical path, makespan per agent cap, peak agents; iterate on edges until the
   makespan is near max(critical path, agent-hours ÷ agents).
9. **Deliver files, then a short summary** (bottom line first: lost-and-restored with ids, added,
   judgment calls to confirm, the one command that regenerates everything).
10. **One pack folder, one zip, never mixed with code.** The project has its own repo. The pack is one
   folder `<PACK>/` (e.g. `FORGEQA/`) at that repo's root, and the zip `<PACK>.zip` contains exactly
   `<PACK>/…`. Every deliverable — spec, screens, tickets, plan, runbook, swimlane, build map, Jira
   import, Cursor rules, tools — is a file in that folder. The pack is **read-only for implementation**:
   code, live contracts and product docs live at the repo root, outside `<PACK>/`. Files that must sit
   at the repo root (Cursor rules, AGENTS.md) ship as templates in `<PACK>/repo-root/` and are installed
   by `<PACK>/bootstrap.sh`, which also seeds the live contracts (OpenAPI, SQL migrations, fixtures,
   bus/config/schema/ports docs, examples, installers) from the pack once. Files shown in the
   conversation are copies of files in the zip.

## 1. Inputs to gather (read all; ask for nothing else)

Conversation history / transcript · earlier pack(s) · newest pack · ticket schema the importer
expects (else use §12) · ticket example · sample harness preamble to beat · sample swimlane/plan
visual to match · architecture documents · stack and platform constraints · team (who runs agents,
agent windows per person, merge windows, who merges) · Jira project key · target repo (`owner/name`)
and pack folder name (`<PACK>`, e.g. FORGEQA).

## 2. Phase 0 — Intake and inventory

1. Unpack every attachment; print a file inventory (path, bytes). Read every text file; extract
   PDFs; view images/decks.
2. `REQUIREMENTS-LEDGER.md`: `R-nnn | statement | source (file:section or "chat: <quote>") | kind
   (feature/rule/constraint/screen/integration/AC/open question) | status (new/kept/lost-in-newest/
   contradicted)`. Expect 150–400 rows. Do not collapse rows.
3. `INPUT-DIFF.md`: what the newest pack changed vs earlier work — stack, features added, features
   lost, tickets removed, scope narrowed, contradictions introduced.

## 3. Phase 1 — Interrogation

`GAP-REPORT.md`: `G-nnn | severity (blocker/major/minor) | what is missing or broken | evidence |
resolution (restore/add/decide/defer) | lands in (ticket ids, filled later)`. Look for: lost
features; stubs/"later"/"TBD"/"stubs allowed" hiding scope; untestable ACs or ACs with no negative/
edge; references to tables/routes/events/files/env keys/fixtures nothing defines; contradictions
(two stacks, two IDs for one thing, two labels for one state); unsafe defaults (secrets in config,
PII in fixtures, cross-tenant reads, unbounded lists, no idempotency, no rate limits, no fail-closed
policy); single-caller assumptions; serialization traps (one folder locking dozens of tickets);
missing ops scope (install/upgrade/backup, observability, docs, security, perf); missing
human-in-the-loop surfaces (review, approve, override, answer, audit).

## 4. Phase 2 — Merge and freeze

`spec/00-FREEZE.md`: one-paragraph product definition; what it is not; the golden record (the one
sentence that defines failure); acceptance queries Q1…Qn with exact call and expected result (at
least: isolation/IDOR, "the bad thing never happens", "the expensive thing never runs when not
applicable", parity across modes); locked spine table (every knob, value, "assumed if blank");
contradictions resolved (numbered, decided); supersession statement for earlier work.

## 5. Phase 3 — Spec pack (self-sufficient for every ticket)

Under `<PACK>/spec/` (rename to the domain, keep the coverage), normative and terse, exact names. A
ticket may only reference what one of these defines:

| file | must contain |
|---|---|
| PRODUCT.md | problem, users, year-one scope (restored + new), later, domain grains, inputs, outputs, data lifecycle |
| FUNCTION-CATALOG.md | every function grouped A…Z with the ticket prefix that delivers it; acceptance queries mapped to tickets |
| MONOREPO.md + PROCESSES.md | repo tree (pack zone + product zone) with a rule per folder, every process/binary, ports, branch/version rules |
| PIPELINE.md / DOMAIN-FLOWS.md | every stage/flow: inputs, work, outputs, side effects, failure handling, re-entry/retry modes, state machines |
| SCHEMA.md (+ addenda) + sql/NNN_*.sql | every table: columns, keys, indexes, tenancy rule, JSONB→schema mapping; idempotent migrations |
| openapi/*.yaml | every route with status codes; pagination, error body, auth/scoping semantics; must parse |
| EVENTS.md | every event: publisher, when, min data, subscribers, forbidden payload content |
| CONFIG-KEYS.md | every env/config key: default, scope, secret y/n; precedence; per-project config schema |
| OBSERVABILITY.md | logging fields, span/attribute budget, metric catalog, alerts |
| AUTH-TENANCY.md | identity source, roles, route rules, isolation semantics (401/403/404), test tokens |
| PORTS.md | every port interface: methods, implementing ticket, fake behaviour |
| FRONTEND.md (when there is a UI) | stack, repo structure, inside-the-app layout, import rules, state model, commands |
| FIXTURES.md + fixtures | test tokens, seed data, HIT/MISS acceptance bodies, tiny systems-under-test, golden sets |
| SCREENS.md | every screen: route, job, binds-to, states; shell nav; UX rules |
| OUTPUTS.md | every artifact the system emits as a rendering of one source |
| INSTALL.md | modes (single box / compose / k8s / cloud), scripts, doctor checks, CI-tested install |
| INTEGRATIONS.md | every external system: adapter interface, implementations, fallbacks, test doubles |
| DOCS-IN-CODE.md | merge-blocking documentation rules |
| EXTENSIONS.md (if data-driven extensions exist) | manifest schema, folder layout, runtime contract, one canonical example folder |
| canonical examples | one real example of every config/manifest/template file the tickets cite |

Contracts that evolve with the code (OpenAPI, SQL migrations, fixtures, events/config/schema/ports
docs, examples, installers) are frozen in the pack and seeded to live locations at the repo root by
`bootstrap.sh` (§8c); tickets edit the live copies.

## 6. Phase 4 — Harness preamble (`<PACK>/spec/CURSOR_PREAMBLE.md`)

Beat the sample. Imperative, numbered: 0 what the product is (one paragraph with a point of view)
· 1 repo layout (read-only pack, live contracts, product zone)/branch/version/one-ticket-one-PR,
contracts-first rule, folder locks and the full append-only shared-file list, UI design-of-record
rule · 2 languages & frameworks locked and what is forbidden · 3 monorepo & shared-code rules · 4
HTTP/auth/tenancy · 5 data access · 6 messaging/mesh · 7 observability, logging, redaction · 8 product
locks as testable statements · 9 same-PR-or-not-done (live API spec, schemas, events, config docs,
docs-in-code) · 10 tests & fixtures (one test per AC, naming, no live vendors) · 11 security & data ·
12 UI rules · 13 definition of done with a RESULT.json shape, commit trailer, PR title, review
checklist. In Cursor the rules (§8c) replace pasting it; it stays as the long form.

## 7. Phase 5 — Tickets (the main deliverable)

**Format.** Exactly the attached schema (else §12). One JSON with all tickets + per-area batch files
+ `TICKETS.md` rendering, all under `<PACK>/tickets/`.

**Paths.** One `layout.py` owns the path model. Every path in every ticket (services/lock units, links,
designLink, paths in what/notes) is repo-root-relative: pack documents as `<PACK>/spec/…`, live
contracts at their live location (`api/openapi/…`, `db/migrations/…`, `docs/contracts/…`,
`fixtures/data/…`, `schemas/…`), code as plain paths (`pkg/lib/…`). The generator rewrites them and
validation fails on any lock path inside `<PACK>/`. Every ticket's notes state the two-zone layout and
every ticket links the runbook. Jira imports cannot attach files, so every UI ticket names its screen
files (`<PACK>/ui/screens/<id>-<slug>.html` + `.png`) in `what`, `userInterface.designLink`,
`userInterface.screens`, `visualBaseline` and `links`.

**Generation.** Write a Python generator: `common.py` (helper filling mechanical defaults and
asserting the bar below), one `t_<area>.py` per area, `deps.py` (dependency edges, lock-folder
overrides, text patches in one place), `build.py` that assembles, validates against the schema,
checks every `blockedByTempIds` exists, detects cycles, computes topological levels, normalizes
`wave:N` labels, rewrites paths, links UI tickets to screens, emits all outputs, fails loudly. Ship it
in `<PACK>/tools/`.

**Per-ticket bar (assert in code):** `summary` ≤ 80 chars; `why` 40–150 words on the consequence of
not doing it; `what` ≥ 60 words with numbered deliverables and exact paths/tables/routes/events/
keys/edge rules; ≥ 3 ACs (typically 4–7) Given/when/then with concrete data, ≥ 1 negative or edge,
exactly one AC naming the test command; `technicalDetails.services[]` = lock units (folders owned),
non-empty and specific; `apiContract`, `dataMigration` (file name), `idempotency`, `configKeys`
(names only), `vendors`, long `implementerNotes`; `environment.testData` names real fixtures;
`releaseNotes` ≤ 280 chars / ≤ 3 impacts; `logging` with required fields and never-log list;
`metrics` where added; `links[]` to the preamble and every spec file used (all must exist);
ui/full_stack tickets carry `userInterface` (screens, routes, states, accessibility, baseline);
`blockedByTempIds` minimal and true.

**Coverage bar.** Platform/skeleton (build, CI, types, util, observability, schema, DB, auth,
bus, secrets, object store, model/vendor router, fixtures, config engine, policy, sandbox, ports) ·
front-end workspace and packages when there is a UI · every API surface · every domain stage/engine ·
every extension/plugin · every integration (recorded-HTTP tests) · every screen · CLI · packaging
(all-in-one, compose, k8s, cloud IaC, CI includes, installers CI-tested) · platform mount/parity if
multi-mode · end-to-end suites with the acceptance queries · security hardening ·
docs/runbooks/ADRs · performance & limits. Typically 100–160 tickets; do not pad, do not merge to
shrink.

**Lock-unit design.** Before the plan, split any folder that would serialize > 4 tickets; declare
shared append-only files in the preamble and rules. Check that no two tickets that can run at the same
time (neither is an ancestor of the other) have overlapping lock paths; fix by narrowing locks or
adding a true dependency.

## 8. Phase 6 — Plan, runbook and visuals (all under `<PACK>/plan/`)

Schedule model (`tools/.../gen_plan.py`): list scheduling on a working clock (08:00–17:00) with
fixed merge windows (default 08:30, 13:00, 17:00 — PRs merge and agents start only then). Size each
ticket S/M/L/XL (default 4/7/11/16 working hours of agent run + review fixes) from ACs, scope words and
lock count, with overrides for E2E/contract/scaffold tickets; a ticket started at 17:00 gets a small
overnight credit for its first autonomous pass. People × agent windows (default 3 × 6); home lane per
person, borrow a free window rather than idle; a window is held until its PR merges. At each window:
merge every green PR, run gates now complete, then start every ticket whose blockers are merged, no
running ticket holds an overlapping lock and a window is free, in priority order (remaining critical
path + 1 h per ticket it unblocks). Gates G0…Gn = checkpoints with runnable checks and an "if red"
action; only the skeleton and the contracts gate block everyone. Report a finish grid: agents per
person × merge cadence (2 windows / 3 windows / continuous).

1. `plan/BUILD_PLAN.md` — **the runbook**: the numbers (tickets, agent-hours, finish, peak, critical
   path); a daily-rhythm table for the merge windows; how to run it (a merge window is the trigger,
   one ticket = one agent = one branch, home lane then borrow, merge order, append-only conflict rule);
   gates with checks; Day 0 (repo, unzip, bootstrap, Jira import); then **every step**: "Step n — Day
   d HH:MM merge window · merge X, Y (green ≈ time) → gate → start A on <person> agent k (size, green ≈,
   merge window, unblocked by / was waiting / borrowed, critical, locks, screens)", queued tickets,
   still running, free windows; per-person agent sequences; trigger table for every ticket (agent,
   size, start window, merge window, start-when, unlocks, gate).
2. `plan/CURSOR_PLAN.md` — agent rules, Day 0, dependency levels (∥ within a level, blockers named).
3. `plan/CURSOR_SWIMLANE.pdf` (+ page-1 PNG), from `plan/schedule.json` (ReportLab + DejaVu TTF):
   page 1 = one row per agent window × working days, merge windows marked, a bar per ticket coloured
   by lane (solid while the agent works, pale while the green PR waits for its window), critical path
   outlined, borrowed dashed, gate lines with non-overlapping labels; page 2 = serial spine, gates,
   parallel batches; page 3+ = step table (#, window, merges, gate, starts); last = per person. Match
   any attached sample's reading logic.
4. `tools/.../next.py --merged <ids> --running <ids>` — prints what can start now, in priority order,
   with the planned person/window, lock holds and free windows.
5. `plan/BUILD_MAP.html` (also published as an artifact, and offered as a standalone file with the
   screen PNGs embedded): Tracker (mark started/merged; start-now list computed with the same rule as
   next.py; next-up; copy/paste merged list), agent timeline, gates with live progress, searchable
   ticket table, detail drawer with blockers/unlocks/locks and screen thumbnails.
6. Screens: one HTML + PNG per screen in `<PACK>/ui/screens/` with `index.html` and `screens.json`
   (id, slug, route, title, tickets, job), rendered from SCREENS.md and the brand; every console
   ticket maps to its screens and every screen to a ticket. Keep any attached board in `ui/board/`.
7. `plan/AGENT_AUDIT.md`, `plan/ESTIMATE.md` (finish grid), `plan/schedule.json`, `plan/graph.json`,
   `plan/PACK-VALIDATION.md` regenerated from the same data by one `make_all.py`.

## 8b. Phase 6b — Jira import (`<PACK>/JIRA_IMPORT.json`)

Jira JSON importer format: `{"users":[], "links":[{"name":"Blocks","sourceId":<blocker>,
"destinationId":<blocked>}], "projects":[{"name","key","type":"software","description",
"components":[lanes], "issues":[{"externalId":tempId, "issueType", "status":"To Do", "priority",
"summary":"[tempId] …", "description", "labels", "components"}]}]}`. Description in Jira wiki
markup (< 32,767 chars; escape `* _ { } [ ] | ^ ~ + # !`; backticks → `{{…}}`): repo-layout panel
("Implement <ID>" start prompt), plan table (owner, agent window, size, start window, merge window,
gate, critical), why, what, ACs as a numbered list, out of scope, technical details (lock folders), UI
design file paths, observability, test data, risks/rollback, references as links to `<repo browse
URL>/<repo-root path>` plus the path, definition of done. Labels without spaces: `temp:<id>`,
`owner:<person>`, `agent:<person>-<n>`, `size:`, `gate:`, `lane:`, `critical-path`, `borrowed`. Also
`tickets/JIRA_IMPORT.csv` (Issue ID, Parent → one epic per lane, repeated Labels and Blocks columns,
Description) and `tickets/JIRA_IMPORT_README.md` (both import paths, field mapping, after-import
assignment).

## 8c. Phase 6c — Cursor rules and bootstrap (no preamble to paste)

`<PACK>/repo-root/.cursor/rules/<project>/*.mdc` (Cursor Project Rules; only `.mdc` is read; YAML
frontmatter `description` (quoted), `globs` (repo-relative, comma-separated), `alwaysApply`) and
`<PACK>/repo-root/AGENTS.md`, generated by `gen_rules.py`: one always-on core rule (layout, how to find
the ticket by temp id in `<PACK>/tickets/*.json`, locks, append-only files, definition of done), glob
rules per area (backend, product locks, front end, screens, live contracts, tests) that `@`-reference
their spec files, and a rule that marks `<PACK>/**` read-only. Each rule < 500 lines.
`<PACK>/bootstrap.sh` installs them and seeds the live contracts without ever overwriting an existing
file (`--rules` refreshes rules, `--check` shows drift). The runbook, Jira descriptions and README tell
people to start agents with `Implement <TEMP_ID>`; the long preamble stays for other harnesses. Tell
the user to confirm once that a cloud agent's context shows the rules.

## 9. Phase 7 — Validation before delivery (do all; fix; re-run)

Schema validation; dependency existence; no cycles; lock-unit conflicts · every `links[].url`
exists; every API path a ticket cites exists in an OpenAPI file; every table exists in SCHEMA or is
declared as a new migration; every event exists in the catalog or is declared as an addition ·
every YAML/JSON/SQL parses, PDFs render, HTML has no console errors · every document a ticket names
exists after bootstrap or is created by that ticket or one of its blockers · no lock path inside
`<PACK>/` · schedule: no two concurrent agents share a lock, nothing starts before its blockers, agent
cap held · JIRA_IMPORT.json: one issue per ticket, every Blocks link resolves, descriptions under the
limit, valid priorities · every UI ticket names existing screen files · run `bootstrap.sh` in a
scratch repo (symlink the pack) and check every ticket link resolves there, rules frontmatter/globs/
@refs are valid, re-running never overwrites a code-owned file · agent walk: 10 random tickets
buildable from ticket + links alone, fix the spec where not · every ledger row dispositioned, every
GAP row names the tickets that close it.

## 10. Phase 8 — Bundle and deliver

Folder `<PACK>/`: `README.md` (two-zone layout, Day 0 incl. bootstrap, read order, how fast, folder
map, how to regenerate) · `bootstrap.sh` · `repo-root/` · `JIRA_IMPORT.json` · `plan/` · `tickets/` ·
`spec/` · `ui/screens/` (+ `ui/board/`) · `jira/` · `examples/` · `install/` · `decks/` · `tools/`
(generators + `layout.py` + `make_all.py` + `next.py` + these prompts). Run `make_all.py` last; it must
print ALL CHECKS PASS. Zip as `<PACK>.zip` containing `<PACK>/…` only (no caches). Send the zip;
optionally also show the runbook, swimlane PDF, Jira file and a standalone build map (copies of what is
in the zip) and publish the build map. Then the short summary.

## 11. Definition of done

- Every attachment read in full; ledger and gap report reconciled
- Newest stack and supplied architecture documents honoured; every earlier capability carried or explicitly dispositioned
- Spec self-sufficient: no ticket references something undefined
- Preamble beats the sample; contains RESULT.json contract and folder-lock rule
- Tickets schema-valid, generator-produced, ≥ 3 ACs with negative/edge + test AC, lock units set, links resolve, no cycles
- Everything in `<PACK>/` and in one zip; nothing a ticket builds lands in `<PACK>/`; every ticket path repo-root-relative; UI tickets name their screen files
- Cursor rules + AGENTS.md generated, installed by bootstrap.sh, validated in a scratch repo
- Runbook with every merge-window step, gates, per-person view and trigger table; next.py; swimlane PDF from the schedule; build-map tracker published
- Finish grid and critical path reported; dependency edges cut until the build is agent-bound, not chain-bound
- JIRA_IMPORT.json (+ CSV fallback) validated
- Audit, estimate, validation regenerated from the same data
- Everything parses; no placeholder; no "TBD" survives without a ticket
- Delivered as files with a bottom-line summary

## 12. Ticket schema (when none is attached)

```json
{ "$schema": "https://json-schema.org/draft/2020-12/schema", "title": "JiraBatchExpanded",
  "type": "object", "required": ["projectKey", "tickets"],
  "properties": {
    "projectKey": {"type": "string", "minLength": 2, "maxLength": 10},
    "defaultIssueType": {"type": "string", "enum": ["Story", "Bug", "Task", "Spike"]},
    "defaultLabels": {"type": "array", "items": {"type": "string"}},
    "source": {"type": "object", "properties": {"prdTitle": {"type": "string"}, "prdVersion": {"type": "string"}, "generatedAt": {"type": "string"}}},
    "tickets": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/ticket"}}},
  "$defs": {
    "link": {"type": "object", "required": ["title", "url"], "properties": {"title": {"type": "string"}, "url": {"type": "string"}}},
    "ac": {"type": "object", "required": ["id", "kind", "text"], "properties": {"id": {"type": "string", "pattern": "^AC-\\d+$"}, "kind": {"type": "string", "enum": ["happy", "negative", "edge", "flag_on", "flag_off", "nfr"]}, "text": {"type": "string"}}},
    "nfr": {"type": "object", "required": ["id", "text"], "properties": {"id": {"type": "string", "pattern": "^NFR-\\d+$"}, "text": {"type": "string"}}},
    "ticket": {"type": "object",
      "required": ["tempId", "summary", "issueType", "layer", "systems", "why", "what", "acceptanceCriteria", "technicalDetails", "releaseNotes", "environment"],
      "properties": {
        "tempId": {"type": "string"}, "summary": {"type": "string", "maxLength": 80},
        "issueType": {"type": "string", "enum": ["Story", "Bug", "Task", "Spike"]},
        "priority": {"type": "string", "enum": ["Highest", "High", "Medium", "Low", "Lowest"]},
        "labels": {"type": "array", "items": {"type": "string"}},
        "layer": {"type": "string", "enum": ["ui", "backend", "full_stack"]},
        "systems": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["system", "component"], "properties": {"system": {"type": "string"}, "component": {"type": "string"}}}},
        "areasProposed": {"type": "array", "items": {"type": "string"}},
        "forgeRepo": {"type": ["string", "null"]}, "forgeMode": {"type": ["string", "null"]},
        "parentTempId": {"type": ["string", "null"]}, "blockedByTempIds": {"type": "array", "items": {"type": "string"}},
        "why": {"type": "string", "minLength": 40}, "what": {"type": "string", "minLength": 20},
        "outOfScope": {"type": "array", "items": {"type": "string"}},
        "acceptanceCriteria": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/ac"}},
        "nfrs": {"type": "array", "items": {"$ref": "#/$defs/nfr"}},
        "technicalDetails": {"type": "object", "required": ["services", "apiContract", "dataMigration", "configKeys"],
          "properties": {"services": {"type": "array", "items": {"type": "string"}}, "apiContract": {"type": "string"}, "dataMigration": {"type": "string"}, "idempotency": {"type": "string"}, "configKeys": {"type": "array", "items": {"type": "string"}}, "vendors": {"type": "array", "items": {"type": "string"}}, "implementerNotes": {"type": "string"}}},
        "featureFlag": {"type": ["object", "null"], "properties": {"name": {"type": "string"}, "owner": {"type": "string"}, "defaults": {"type": "object"}, "rolloutPlan": {"type": "string"}, "killSwitch": {"type": "string"}, "behaviorWhenOff": {"type": "string"}, "cleanupTicketTempId": {"type": ["string", "null"]}}},
        "releaseNotes": {"type": "object", "required": ["title", "description", "audience", "visibility"], "properties": {"title": {"type": "string"}, "description": {"type": "string", "maxLength": 280}, "impacts": {"type": "array", "maxItems": 3, "items": {"type": "string"}}, "audience": {"type": "string", "enum": ["customer", "internal", "both"]}, "visibility": {"type": "string", "enum": ["announce", "silent"]}}},
        "userInterface": {"type": ["object", "null"], "properties": {"screens": {"type": "array", "items": {"type": "string"}}, "routes": {"type": "array", "items": {"type": "string"}}, "designLink": {"type": ["string", "null"]}, "states": {"type": "array", "items": {"type": "string"}}, "accessibility": {"type": "string"}, "browsers": {"type": "array", "items": {"type": "string"}}, "visualBaseline": {"type": "string"}}},
        "logging": {"type": "object", "properties": {"events": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "level": {"type": "string"}, "when": {"type": "string"}, "fields": {"type": "array", "items": {"type": "string"}}}}}, "requiredFieldsEveryLine": {"type": "array", "items": {"type": "string"}}, "neverLog": {"type": "array", "items": {"type": "string"}}, "retention": {"type": "string"}}},
        "metrics": {"type": "object", "properties": {"metrics": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "type": {"type": "string"}, "labels": {"type": "array", "items": {"type": "string"}}}}}, "dashboard": {"type": "string"}, "alerts": {"type": "array", "items": {"type": "string"}}, "sloTouched": {"type": "string"}}},
        "analyticsEvents": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "when": {"type": "string"}, "attributes": {"type": "array", "items": {"type": "string"}}, "consumer": {"type": "string"}}}},
        "environment": {"type": "object", "required": ["name", "testData"], "properties": {"name": {"type": "string"}, "testData": {"type": "string"}}},
        "dependenciesRisks": {"type": "object", "properties": {"dependsOn": {"type": "array", "items": {"type": "string"}}, "vendorsInTest": {"type": "array", "items": {"type": "string"}}, "risks": {"type": "string"}, "rollback": {"type": "string"}}},
        "notes": {"type": "string"}, "links": {"type": "array", "items": {"$ref": "#/$defs/link"}}}}}}
```

## 13. Style

Terse, imperative, exact. No marketing prose, no restating the request. Every sentence in a ticket
must help an agent decide what to build or how to prove it. Use the product's real names. When you
make a judgment call, say so in one line and move on.

## Fill-in (read from `$ARGUMENTS` or the conversation)

PROJECT_NAME · ONE-SENTENCE JOB OF THE SYSTEM · STACK LOCKS (or "take from newest pack") ·
ARCHITECTURE DOCUMENTS · HARNESS (Cursor Cloud Agents | Claude Code | both) · JIRA PROJECT KEY · REPO
(`owner/name`) + PACK FOLDER (`<PACK>`, e.g. FORGEQA) · TEAM (names, agent windows per person, merge
windows, who merges) · ATTACHMENTS · THINGS EXPLICITLY CUT (do not restore) · DECISIONS ALREADY MADE
(do not revisit).