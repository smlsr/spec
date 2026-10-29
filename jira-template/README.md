# HOS Jira ticket template

One ticket = one agent = one branch = one pull request. The ticket plus the spec files it links must be enough for an agent that
knows nothing to build it and prove it, so every field below is mandatory unless marked optional, and `tools/check_tickets.py`
fails the batch when a ticket misses the bar. Tickets are written by generator scripts from the spec pack, never by hand in Jira.

## The bar

| Field | Rule | Why it matters |
|---|---|---|
| `tempId` | Plan id, unique across every program in the Jira project (`Q-45`, `AD-15`, `C-71`) | Becomes Jira `externalId`; Warp, branches, PR titles and test names all key on it |
| `summary` | 80 characters or fewer | Rendered `<ID> · <summary>` in Jira |
| `why` | 40–150 words: the consequence of not building it | How the agent chooses between two reasonable implementations |
| `what` | 60+ words, numbered deliverables, exact paths, tables, routes, events, keys | No guessing names; reviewers check the list |
| `acceptanceCriteria` | 3+ Given/When/Then with real fixture data; at least one `negative` or `edge`; exactly one whose text starts `Test command:` | One test per AC; the one command must exit 0 before the PR opens |
| `technicalDetails.services` | The lock units: folders or files this ticket owns | Two running agents never share a lock, so up to 18 can run at once |
| `technicalDetails.*` | `apiContract`, `dataMigration`, `idempotency`, `configKeys` (names from CONFIG-KEYS), `vendors`, `implementerNotes` | Contracts first; keys and migrations that nothing defines are caught |
| `blockedByTempIds` | Minimal and true; every id exists; no cycles | Becomes Jira **Blocks** links and the build schedule |
| `userInterface` (ui) | `designLink` + `screens` (the mock file and PNG), `routes`, `states`, `accessibility`, `visualBaseline` | The screen is the design of record; Jira cannot attach files, so paths are named |
| Clickables (ui) | Every click that opens, navigates or runs a function has an AC or a test (rule `45-ui-clicks`) | Agents leave handlers unwired; later edits break them |
| `links` | Every spec page the ticket relies on (preamble, SCREENS, openapi, EVENTS…); each must exist | Truth grounded in the spec, not in the agent's guess |
| `environment.testData` | Real fixture files | Tests run on fixtures, never live vendors |
| `releaseNotes`, `logging`, `labels` | ≤ 280-char note; log events, required fields, never-log list; `module:`, `size:`, `gate:`, `lane:` labels | Ops and Warp (size → model, gate → block) read them |

Full schema: `ticket.schema.json` (title `ForgeQaJiraBatchExpanded`). Blank starting point: `ticket-template.json`.
A real one: `examples/Q-45.ticket.json` → `examples/Q-45.jira-description.txt` (what Jira shows) → `examples/Q-45.jira-import.json`.

## How a ticket renders in Jira (description, wiki markup)

```
*Module:* APP · *Layer:* ui · *Repo:* HumanifyOS-UI · *Size:* M · *Gate:* G2
*UI screen:* [<mock>.html|<mock>.html] (routes /voc#sec-emerging)

h3. Why            … the why …
h3. What           … numbered deliverables …
h3. Out of scope   * …
h3. Acceptance criteria
* *AC-1* (happy): Given … when … then …
* *AC-6* (happy): Test command: {{pnpm --filter quality test -- voc/emerging}}
h3. Technical details
* *Lock units:* {{apps/web/quality/src/modules/voc/emerging}}, …
* *API contract:* GET /v1/app/cx/emerging (vocEmerging)
* *Migration:* none · *Idempotency:* … · *Config keys:* … · *Vendors:* … · *Implementer notes:* …
*Blocked by:* Q-00, Q-02, Q-04, Q-61, Q-16, A-53
h3. Links          * [CURSOR_PREAMBLE.md|…] * [SCREENS.md|…] …
```

## Jira Cloud import rules (standing)

1. **No `reporter`.** 2. **`status` is "To Do".** 3. **No `customFieldValues`** — Story Points is a locked field in Jira Cloud; size
travels as the `size:` label. 4. **Project name** comes from config (`--name`, e.g. "Humanify OS", key `HOS`). 5. **No `created`.**
Also: `externalId` = the plan id; summary `<ID> · <summary>`; every `blockedByTempIds` edge is a `Blocks` link (blocker → blocked);
issues are written blockers-first; descriptions stay under 32,767 characters; all programs load into one project with no
duplicate `externalId` (case-insensitive). `tools/to_jira.py` applies every rule.

## Jira flow (Warp)

To Do → In Progress (claimed) → In Review (Bugbot requested) → QA Ready (sizes outside `autoMergeSizes`, default L and XL, wait
for approval) → Done (merged). Warp's `/warp-scan` maps each issue back to its plan id through the External ID field, a
`warp:<id>` label or a remote link.
