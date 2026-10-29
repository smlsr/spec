#!/usr/bin/env python3
"""to_jira.py — turn a ticket batch into a Jira Cloud JSON import (Jira's "Import issues from JSON").

Usage:  python3 tools/to_jira.py tickets.json --name "Humanify OS" --key HOS [--out JIRA_IMPORT.json]

Jira Cloud import rules (HOS, standing):
  1. no reporter          2. status "To Do"         3. no customFieldValues (Story Points is a locked field in Jira Cloud)
  4. project name from --name                       5. no created date
  externalId = the plan id (tempId), summary "<ID> · <summary>", every blockedByTempIds edge → a "Blocks" link
  (blocker → blocked). Issues are written blockers-first so every link resolves during the import.
The description is Jira wiki markup: header line, UI screen, Why, What, Out of scope, Acceptance criteria, Technical details
(lock units, API contract, migration, idempotency, config keys, vendors, implementer notes), Blocked by, Links.
Run tools/check_tickets.py first. Standard library only.
"""
import json, re, sys, argparse

FORBIDDEN = ("reporter", "created", "customFieldValues")


def wiki(md):
    if not md: return ""
    t = str(md)
    t = re.sub(r"```[a-z]*\n(.*?)```", lambda m: "{code}" + m.group(1) + "{code}", t, flags=re.S)
    t = re.sub(r"`([^`\n]+)`", lambda m: "{{" + m.group(1).replace("{", "(").replace("}", ")") + "}}", t)
    t = re.sub(r"\*\*([^*\n]+)\*\*", r"*\1*", t)
    t = re.sub(r"^### (.+)$", r"h4. \1", t, flags=re.M)
    t = re.sub(r"^## (.+)$", r"h3. \1", t, flags=re.M)
    t = re.sub(r"^(\d+)\. ", "# ", t, flags=re.M)
    t = re.sub(r"^- ", "* ", t, flags=re.M)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1|\2]", t)
    return t


def label(t, prefix):
    return next((l.split(":", 1)[1] for l in t.get("labels") or [] if l.startswith(prefix + ":")), "")


def describe(t):
    td, ui, acs = t.get("technicalDetails") or {}, t.get("userInterface") or {}, t.get("acceptanceCriteria") or []
    head = [f"*Module:* {label(t, 'module').upper() or '—'}", f"*Layer:* {t.get('layer')}", f"*Repo:* {t.get('forgeRepo') or '—'}"]
    if label(t, "size"): head.append(f"*Size:* {label(t, 'size')}")
    if label(t, "gate"): head.append(f"*Gate:* {label(t, 'gate')}")
    P = [" · ".join(head), ""]
    if ui.get("designLink"):
        P += [f"*UI screen:* [{ui['designLink']}|{ui['designLink']}]" + (f" (routes {', '.join(ui.get('routes') or [])})" if ui.get("routes") else ""), ""]
    P += ["h3. Why", wiki(t.get("why")), "", "h3. What", wiki(t.get("what")), ""]
    if t.get("outOfScope"): P += ["h3. Out of scope"] + ["* " + wiki(x) for x in t["outOfScope"]] + [""]
    P += ["h3. Acceptance criteria"] + [f"* *{a.get('id', 'AC')}* ({a.get('kind', '')}): {wiki(a.get('text', ''))}" for a in acs] + [""]
    P += ["h3. Technical details",
          "* *Lock units:* " + (", ".join("{{" + u + "}}" for u in td.get("services") or []) or "—"),
          "* *API contract:* " + wiki(td.get("apiContract") or "none"),
          "* *Migration:* " + wiki(td.get("dataMigration") or "none"),
          "* *Idempotency:* " + wiki(td.get("idempotency") or "n/a"),
          "* *Config keys:* " + (", ".join(td.get("configKeys") or []) or "—"),
          "* *Vendors:* " + (", ".join(td.get("vendors") or []) or "—")]
    if td.get("implementerNotes"): P.append("* *Implementer notes:* " + wiki(td["implementerNotes"]))
    if t.get("nfrs"): P += ["", "h3. NFRs"] + ["* " + wiki(x.get("text") if isinstance(x, dict) else x) for x in t["nfrs"]]
    if t.get("notes"): P += ["", "h3. Notes", wiki(t["notes"])]
    if t.get("blockedByTempIds"): P += ["", "*Blocked by:* " + ", ".join(t["blockedByTempIds"])]
    P += ["", "h3. Links"] + [f"* [{l.get('title', l.get('url'))}|{l.get('url')}]" for l in t.get("links") or []]
    d = "\n".join(P)
    if len(d) > 32000: d = d[:31900] + "\n\n(truncated — the full ticket is in the pack)"
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickets"); ap.add_argument("--name", required=True); ap.add_argument("--key", required=True)
    ap.add_argument("--out", default="JIRA_IMPORT.json")
    a = ap.parse_args()
    data = json.load(open(a.tickets, encoding="utf-8"))
    tickets = data["tickets"] if isinstance(data, dict) else data
    T = {t["tempId"]: t for t in tickets}
    order, seen = [], set()
    def place(i, stack=()):                       # blockers first, so every Blocks link resolves during the import
        if i in seen: return
        if i in stack: sys.exit(f"to_jira: cycle through {i}")
        for b in T[i].get("blockedByTempIds") or []:
            if b in T: place(b, stack + (i,))
        seen.add(i); order.append(i)
    for t in tickets: place(t["tempId"])
    issues, links = [], []
    for i in order:
        t = T[i]
        issues.append({"externalId": i, "summary": f"{i} · {t['summary']}", "issueType": t.get("issueType") or "Story",
                       "priority": t.get("priority") or "Medium", "status": "To Do",
                       "labels": sorted(set(t.get("labels") or []) | {f"layer:{t.get('layer')}"}),
                       "components": [label(t, "module").upper()] if label(t, "module") else [],
                       "description": describe(t)})
        links += [{"name": "Blocks", "sourceId": b, "destinationId": i} for b in t.get("blockedByTempIds") or [] if b in T]
    for x in issues:
        assert not any(k in x for k in FORBIDDEN)
    comps = sorted({c for x in issues for c in x["components"]})
    out = {"projects": [{"name": a.name, "key": a.key, "type": "software", "components": [{"name": c} for c in comps], "issues": issues}], "links": links}
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"to_jira: {len(issues)} issues, {len(links)} Blocks links → {a.out} (project {a.name}, key {a.key}; status To Do; no reporter/created/customFieldValues)")


if __name__ == "__main__":
    main()
