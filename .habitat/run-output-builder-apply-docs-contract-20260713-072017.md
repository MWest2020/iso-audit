# Habitat builder — apply-docs-contract

_run_id builder-apply-docs-contract-20260713-072017 · verdict ok · 2026-07-13T07:31:47Z_

---

Committed. Task 4.1 (open the PR) I cannot complete directly: `gh` is not installed and pushing/PR creation belongs to the habitat-harness (task 1.1). I've left 4.1 unchecked and stopped there. Here is the run report.

## Run report — `apply-docs-contract`

**Status:** implemented and committed on `habitat/builder/apply-docs-contract` (commit `66f4309`). Push + PR creation deferred to the harness/Mark.

### What I did
Migrated the flat `docs/` layout (16 pages) to the Diátaxis-light contract:

| New location | Pages |
|---|---|
| `docs/index.md` | new English entry page (`status: draft`) |
| `docs/explanation/` | `missie.md`, `memo-architecture.md`, `compensating-control.md` |
| `docs/reference/` | `modes.md`, `source-{drive,jira,mcp,planning,rest}.md`, `sinks.md`, `notifier-{email,mattermost,slack,teams}.md` |
| `docs/how-to/` | `miro-auditor-bord-prompt.md`, `miro-interview-prompt.md` |

- Submaps flattened with prefixes (`source-*`, `notifier-*`) per the repo-specific rule.
- Front matter on **every** page (`status` + `last_reviewed: 2026-07-13`, no `owner`). Migrated-without-review = `draft`.
- Old paths kept as `status: deprecated` redirect stubs (16) so inbound links keep working.
- Intra-docs links repointed to canonical locations; all relative links verified to resolve.
- `.mcp.json` was already seeded in root with the `TODO-change-3` placeholder — unchanged, task satisfied.
- No content translated; no changes outside `docs/` + `tasks.md`. No secrets.

### Three points flagged for the PR body / Mark's decision
1. **Language (proposal-flagged):** migrated pages remain **Dutch** as instructed; only new pages (index + stub headers) are English. Decision for Mark: translate to English, or make the repo private.
2. **Stubs vs. the strict contract:** the reviewer's contract summary says "only index/how-to/reference/explanation carry markdown," but the proposal's stub clause plus CLAUDE.md's un-editable mandatory link to `docs/missie.md` require leaving deprecated stubs at old paths. I chose stubs (reversible; delete once inbound links in README/ARCHITECTURE/etc. are updated in a follow-up). Note this tension when reviewing.
3. **`.github` convention drift:** issue/PR templates still reference `docs/sources/<naam>.md` / `docs/notifiers/<naam>.md` conventions — out of scope here, worth a follow-up to point them at `reference/source-*` / `reference/notifier-*`.

### Ready-to-use PR

**Title:** `docs: apply handbook docs contract`

**Body:**
```markdown
Applies the handbook docs contract (change `apply-docs-contract`, wave 2).

Contract points applied:
- [x] docs/index.md + how-to/ + reference/ + explanation/ structure
- [x] empty dirs omitted (no adr/ yet); minimum viable met
- [x] front matter (status + last_reviewed) on every page; no owner field
- [x] migrated-without-review pages = status: draft, last_reviewed 2026-07-13
- [x] README kept; docs/index.md links to it, does not replace it
- [x] existing docs migrated; deprecated redirect stubs left at old paths
- [x] .mcp.json in root with TODO-change-3 placeholder (seeded, unchanged)
- [x] sources/sinks/notifiers flattened under reference/ with prefixes
- [x] missie/memo-architecture/compensating-control -> explanation/;
      modes -> reference/; miro prompts -> how-to/

Deferred to maintainer:
- **Language:** migrated pages are still Dutch (not translated, per proposal).
  Decision needed: translate to English or make the repo private.
- **Stubs:** old paths remain as `status: deprecated` redirect stubs so
  inbound links (incl. CLAUDE.md's mandatory docs/missie.md pointer) keep
  working. Remove them in a follow-up once README/ARCHITECTURE/CLAUDE/.github
  links are repointed — that link/template update is out of this change's scope.

STOP: Mark merges.
```

Everything except the actual push/PR-open (harness-owned, `gh` unavailable here) is done.
