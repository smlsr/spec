# Coding skill packs to import under the HOS rules

Layering: imported coding discipline (below) → your coding requirements (`10-backend` / `10-frontend`, stack locks, tenancy,
security) → spec-pack rules (`AGENTS.md`, program pages, module and topic rules, `40-ticket`, `45-ui-clicks`) → the ticket.
Commit vendored copies to `.cursor/skills/` (cloud agents only see committed skills), pinned to a commit, refreshed quarterly.
Stars are from the ecosyste.ms GitHub mirror, October 2026.

| Pack | Repo | License · stars | What it adds | Import |
|---|---|---|---|---|
| Ponytail | github.com/DietrichGebert/ponytail | MIT · ~178k | Stops over-building: reuse, stdlib or native feature first, then minimum code; keeps validation, security, a11y and tests on risky logic. Skills: `ponytail`, `-review`, `-audit`, `-debt` | copy `.cursor/rules/ponytail.mdc` + `skills/ponytail*` into the repo, or `npx skills add DietrichGebert/ponytail --skill '*'` |
| Superpowers | github.com/obra/superpowers | MIT · ~305k | `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `writing-plans`, `subagent-driven-development` (spec-compliance review, then code quality), code review skills | Cursor `/add-plugin superpowers`; for cloud agents copy `skills/*` into `.cursor/skills/` |
| Spec Kit | github.com/github/spec-kit | MIT · ~144k | Spec workflow: constitution → specify → plan → tasks → implement (+ clarify, analyze, bug extensions) | `uv tool install specify-cli` then `specify init . --integration cursor-agent` |
| (or) OpenSpec | github.com/Fission-AI/OpenSpec | MIT · ~73k | Lighter, change-proposal flow for existing code — pick Spec Kit or OpenSpec, not both | `npm i -g @fission-ai/openspec@latest` then `openspec init` |
| Agent Skills | github.com/addyosmani/agent-skills | MIT · ~110k | Review gates: `code-review-and-quality`, `security-and-hardening` (OWASP, secrets, dependencies), `doubt-driven-development`; `/ship` runs code, test, security and performance reviewers in parallel | `npx skills add addyosmani/agent-skills` |
| Anthropic skills | github.com/anthropics/skills | mostly Apache-2.0 · ~183k | `skill-creator`: the template for writing your own spec-pack skills | copy `skills/skill-creator` |
