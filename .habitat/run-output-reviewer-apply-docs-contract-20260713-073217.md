# Habitat reviewer — apply-docs-contract

_run_id reviewer-apply-docs-contract-20260713-073217 · verdict ok · 2026-07-13T07:34:53Z_

---

I have everything needed. Migration is faithful (identical structure), harness artifacts carry no secrets, cage intact.

---

# Reviewer verdict: **PASS** ✅

Change `apply-docs-contract` on `habitat/reviewer/apply-docs-contract`. Read-only review against `CLAUDE.md` + the change. No fixes applied.

## Check 1 — Scope ✓
- `docs/` restructured per the repo-specific plan: `sources|sinks|notifiers → reference/` (flattened with prefixes), `missie|memo-architecture|compensating-control → explanation/`, `modes → reference/`, both miro prompts → `how-to/`. Migrations are faithful (e.g. `reference/modes.md` has byte-identical heading structure to the old `modes.md`).
- `.mcp.json` placed at root with the `TODO-change-3` placeholder intact (task 2.4). ✓
- `tasks.md` checkboxes 1.1–3.1 marked done; 4.1 (PR) correctly left open — builder stops before PR. ✓
- Out-of-change files in the diff — `.habitat/audit.jsonl`, `.habitat/run-*.md/.html`, `run-report.json` — are **habitat-harness bookkeeping**, not builder-authored source. Not a builder scope violation; noted for transparency.

## Check 2 — Contract ✓
- Canonical content lives only in `index.md` + `how-to/` + `reference/` + `explanation/`; `reference/` is flat with prefixes (`notifier-slack.md`, `source-drive.md`) — submaps correctly avoided. ✓
- Every one of the 34 pages has front matter with `status` (valid enum) + `last_reviewed: 2026-07-13`. Migrated-without-review = `draft`, old-location stubs = `deprecated`. **No `owner` front-matter field** anywhere (the `grep` hits are prose "repo-owner" in pre-existing migrated content). ✓
- `index.md`: one-paragraph what-it-is, status line, README link, section links. ✓

**Two authorized deviations — flag for Mark's merge decision, not failures:**
1. **Stubs outside the allowed dirs.** Old-location `.md` stubs remain (top-level + `notifiers/ sources/ sinks/`). The proposal explicitly mandates this ("stub met verwijzing achterlaten"), and `docs/missie.md`, `docs/miro-auditor-bord-prompt.md`, `docs/miro-interview-prompt.md` are linked from `CLAUDE.md` (which this change may not touch) — so those stubs are strictly required to avoid broken links. All stub targets resolve. A handbook aggregator should filter `status: deprecated` so these don't surface as duplicates.
2. **Mixed language.** Repo is Dutch (migrated) + English (new `index.md`). The proposal explicitly says *do not translate in this change* and defer to Mark; `index.md` documents this. New content is English per the contract. (Task 3.1's parenthetical "één taal (English)" is superseded by the proposal's explicit deferral.)

## Check 3 — Cage intact ✓
No changes to `CLAUDE.md`, `.claude/agents/`, or any CI config.

## Check 4 — No secrets ✓
All `token`/`secret`/`password` matches are env-var **names** (`SLACK_BOT_TOKEN`, `JIRA_TOKEN`, `ISO_AUDIT_SMTP_PASS`), format placeholders (`xoxb-…`, `<je Miro API token>`), and prose — all pre-existing migrated content. `.mcp.json` URL is the `TODO-change-3` placeholder. Harness artifacts scanned clean.

**Bottom line:** contract correctly applied; the two deviations are both explicitly sanctioned by the proposal and belong in the PR body (task 4.1) for Mark. Ready to merge after the PR is opened.
