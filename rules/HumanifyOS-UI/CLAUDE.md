# CLAUDE.md — HumanifyOS-UI · HOSPACK

@AGENTS.md

Claude Code only (everything else is `AGENTS.md`):
- **Program page first**: the router names `.cursor/rules/02-program-<slug>.mdc` — read it, then every file it lists with `@` (paths from the repository root). Topic rules `.cursor/rules/3x-*.mdc` and the ticket protocol `40-ticket.mdc` are read the same way when the task needs them.
- **Module preambles** load by themselves: the `CLAUDE.md` in each module folder imports its module's preamble when you work there.
- **Skills**: `.claude/skills/hos-frontend/SKILL.md`, `.claude/skills/hosadmin-admin/SKILL.md`, `.claude/skills/hosui-app/SKILL.md` — use your program's.
