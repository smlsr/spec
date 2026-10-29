#!/usr/bin/env python3
"""check_tickets.py — hold every ticket to the HOS bar before it goes to Jira.

Usage:  python3 tools/check_tickets.py tickets.json [--schema jira-template/ticket.schema.json]

The input is a ticket batch in the ForgeQaJiraBatchExpanded shape (jira-template/ticket.schema.json):
{"projectKey": "HOS", "tickets": [ {tempId, summary, why, what, acceptanceCriteria, technicalDetails, ...}, ... ]}

Checks (exit 1 on any failure, every failure printed):
  schema          the JSON schema, when the `jsonschema` package is installed (pip install jsonschema); skipped otherwise
  ids             tempId present and unique (also case-insensitively: Jira externalIds collide that way)
  summary         80 characters or fewer
  why             40–150 words — the consequence of not building it
  what            60+ words — numbered deliverables with exact paths, tables, routes, events
  ACs             3+ acceptance criteria; at least one of kind negative or edge; exactly one AC whose text starts
                  "Test command:" (older packs without that prefix: at least one AC names the runner — go test, pnpm, make …)
  lock units      technicalDetails.services non-empty (the folders this agent owns)
  blockers        every blockedByTempIds id exists in the batch (--partial: a warning); no self-block; no cycle
  links           at least one link (the preamble / the spec pages the ticket relies on)
  ui (warning)    a ui / full_stack ticket names a screen (userInterface.designLink or userInterface.screens)
  clicks (warning) a ui ticket whose what mentions click / opens / navigates has at least one AC that clicks (45-ui-clicks)
  --strict        turns the warnings into failures (use it for new packs)
Standard library only.
"""
import json, re, sys, argparse, collections


def words(s): return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’./:_\-]*", s or ""))


RUNNER = re.compile(r"(go test|pnpm|npx|make |vitest|playwright|python3|tools/db_check|spec/sql/tests)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickets")
    ap.add_argument("--schema", default=None)
    ap.add_argument("--partial", action="store_true", help="the batch is a subset: blockers outside it are warnings")
    ap.add_argument("--strict", action="store_true", help="treat warnings (ui screen, click ACs) as failures")
    a = ap.parse_args()
    data = json.load(open(a.tickets, encoding="utf-8"))
    tickets = data["tickets"] if isinstance(data, dict) else data
    E, W = [], []

    if a.schema:
        try:
            import jsonschema
            for err in jsonschema.Draft202012Validator(json.load(open(a.schema, encoding="utf-8"))).iter_errors(data):
                E.append(f"schema: {'/'.join(map(str, err.path))}: {err.message}")
        except ImportError:
            print("check_tickets: jsonschema not installed — schema check skipped (pip install jsonschema)")

    ids = [t.get("tempId") for t in tickets]
    for i, n in collections.Counter(ids).items():
        if not i: E.append("a ticket has no tempId")
        elif n > 1: E.append(f"{i}: duplicate tempId")
    for i, n in collections.Counter((x or "").lower() for x in ids).items():
        if i and n > 1 and ids.count(i) < n: E.append(f"{i}: tempIds differ only in case (Jira externalId collision)")
    known = set(ids)

    for t in tickets:
        tid = t.get("tempId", "?")
        def bad(msg): E.append(f"{tid}: {msg}")
        if len(t.get("summary", "")) > 80: bad(f"summary is {len(t['summary'])} chars (max 80)")
        w = words(t.get("why"))
        if not 40 <= w <= 150: bad(f"why is {w} words (40–150)")
        if words(t.get("what")) < 60: bad(f"what is {words(t.get('what'))} words (60+)")
        acs = t.get("acceptanceCriteria") or []
        if len(acs) < 3: bad(f"{len(acs)} ACs (3+)")
        if not any(x.get("kind") in ("negative", "edge") for x in acs): bad("no negative or edge AC")
        tc = [x for x in acs if (x.get("text") or "").lstrip().startswith("Test command:")]
        if tc:
            if len(tc) != 1: bad(f"{len(tc)} 'Test command:' ACs (exactly 1)")
        elif not any(RUNNER.search(x.get("text") or "") for x in acs):   # older packs: an AC that names the runner
            bad("no test-command AC ('Test command: <cmd>')")
        if not ((t.get("technicalDetails") or {}).get("services")): bad("technicalDetails.services (lock units) is empty")
        for b in t.get("blockedByTempIds") or []:
            if b == tid: bad("blocks itself")
            elif b not in known:
                (W.append(f"{tid}: blocked by {b}, outside this batch") if a.partial else bad(f"blocked by {b}, which is not in this batch"))
        if not t.get("links"): bad("no links to the spec")
        ui = t.get("userInterface") or {}
        if t.get("layer") in ("ui", "full_stack") and not (ui.get("designLink") or ui.get("screens")):
            W.append(f"{tid}: ui ticket names no screen (userInterface.designLink / screens)")
        if t.get("layer") in ("ui", "full_stack") and re.search(r"\b(click|opens?|navigat)", t.get("what") or "", re.I):
            if not any(re.search(r"\bclick", x.get("text") or "", re.I) for x in acs):
                W.append(f"{tid}: the what describes clickable behaviour but no AC clicks (rule 45-ui-clicks)")

    # cycles
    G = {t.get("tempId"): [b for b in t.get("blockedByTempIds") or [] if b in known] for t in tickets}
    state = {}
    def visit(n, path):
        if state.get(n) == 1: E.append(f"cycle: {' → '.join(path + [n])}"); return
        if state.get(n) == 2: return
        state[n] = 1
        for b in G.get(n, []): visit(b, path + [n])
        state[n] = 2
    for n in G: visit(n, [])

    if W:
        print("\n".join("check_tickets: warning: " + w for w in W))
        if a.strict: E += W
    if E:
        print("\n".join("check_tickets: " + e for e in E)); print(f"check_tickets: {len(E)} failure(s) in {len(tickets)} tickets"); sys.exit(1)
    print(f"check_tickets: {len(tickets)} tickets, all checks pass" + (f" ({len(W)} warning(s); --strict fails on them)" if W else ""))


if __name__ == "__main__":
    main()
