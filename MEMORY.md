# MEMORY — iso-audit handoff voor volgende sessie

> Laatste update: 2026-05-20 · branch `refactor/iso-audit-milestone-b`
>
> Dit document is een handoff-snapshot, geen log. Werk het bij aan het
> einde van elke sessie met (a) waar je gebleven bent en (b) wat de
> volgende sessie als eerste oppakt.

## Repo-status

| Component | Status |
|---|---|
| Milestone A (skeleton + 3 protocollen) | ✓ klaar, op `main` |
| Milestone B (verhuizing + classifier + reporting) | ✓ klaar, gemerged in `refactor/iso-audit-milestone-b` |
| Milestone C §3.1-3.5 (modes, notifiers, sinks, sources, CLI) | ✓ klaar, op `refactor/iso-audit-milestone-b` |
| Milestone C §3.6 (eerste integer-run, acceptatie) | ⏳ wacht op manuele runs met Slack/Email/Jira creds |
| Milestone C §3.7 (cleanup `Ops_to_Biz/audit/`) | ✓ klaar — Ops_to_Biz commits `2edc146` + `512c49a` |
| Milestone C §3.8 (tag `v1.0.0`) | ⏳ na §3.6 acceptatie |
| Open PR #9: `miro-write-trim` | ⏳ wacht op review/merge — alle gates groen |

**Test/quality baseline op huidige branch:** 682 passed, 1 skipped,
81% coverage, ruff/mypy --strict/bandit clean.

**Na merge van PR #9:** 649 passed, 85% coverage.

## Open PR #9 — miro-write-trim

Branch: `refactor/miro-write-trim` → `refactor/iso-audit-milestone-b`.
Verwijdert `iso_audit.miro.{board_setup,interview}` + tests; behoudt
`client` + `ingest` (READ-pijp). Vervangt write-pad door Miro-AI
prompts in `docs/miro-auditor-bord-prompt.md` en
`docs/miro-interview-prompt.md`.

**Gouden test geslaagd:** `iso-audit pipeline --source drive --norm
9001 --mode autonoom --dry-run-cost --rehash` geeft byte-identiek
152 docs / 73 calls / $0.3339 op trim-branch als op baseline.

OpenSpec: `openspec/changes/miro-write-trim/` (proposal + design +
tasks + spec-delta). Na merge naar archive verplaatsen.

## Volgende sessie: Jira-integratie afmaken

`JiraSource` werkt al (17 tests, 91% cov, contract-tests groen) maar
is nog niet live gevalideerd. Plan in 5 stappen:

### Stap 1 — Smoke-test live Jira

1. Zet in `.env`: `JIRA_BASE_URL=https://conduction.atlassian.net`,
   `JIRA_EMAIL=<user>`, `JIRA_API_TOKEN=<token uit id.atlassian.com>`.
2. `uv run iso-audit doctor` → verifieer `jira` healthcheck = ok
   met `tenant` en `user`-naam in output.
3. `uv run iso-audit pipeline --source jira --norm 9001
   --mode autonoom --dry-run-cost` → noteer aantal issues +
   kosten-schatting.

### Stap 2 — JQL afstemmen

`JIRA_JQL` env-var override de default. Vraag aan Mark: welke
projecten + labels zijn de echte audit-scope? Voorbeelden van mogelijke
filters:

- Per project: `project = ISO`
- Per label-set: `labels in (iso27001, iso9001, compliance)` (default
  in `JiraSource.list_findings`)
- Status: `statusCategory != Done` (alleen open items)

Combineer met `JIRA_FINDINGS_JQL` voor de `list_findings()`-iterator
specifiek (bewijs-issues, niet alle metadata-issues).

### Stap 3 — Label → clausule heuristiek verfijnen

Huidige map in `src/iso_audit/sources/jira.py:_label_naar_clausule`:

- `iso27001-5.30` → clausule `5.30`
- `iso9001-9.1` → `9.1`
- Andere labels → leeg → geen clause-match

Check met Mark of Conduction's label-conventie hierop aansluit. Zo
niet: aanpassen + 1-2 extra tests in `tests/sources/test_jira.py`.

### Stap 4 — Audit-trail koppeling

Verifieer dat `classifications.finding_id` voor jira-ingest de vorm
`jira:<sessie_id>:<issue-key>` krijgt (zie `findings.py` → wordt
`finding_id` uit `Finding.id` afgeleid?). Zo niet, expliciet maken
zodat een Jira-issue traceerbaar terug te vinden is in de audit-trail.

### Stap 5 — Eerste integer-run end-to-end

Zodra Jira-bevindingen er zijn, draaien:

```bash
uv run iso-audit pipeline --source drive --source jira --norm 9001 \
  --mode integer --notifier slack
```

Vereist `SLACK_WEBHOOK_URL` of `SLACK_BOT_TOKEN+SLACK_CHANNEL_ID` in
`.env`. Voor email-pad: `SMTP_HOST/USER/PASSWORD/FROM` +
`AUDIT_NOTIFIER_EMAIL` (plus de Flask-portaal die nog niet bestaat —
opgeschort naar eigen change-proposal, zie tasks.md §3.2.6-7).

Acceptatie-checklist staat in `openspec/changes/archive/iso-refactor/
tasks.md` §3.6.1-5.

## Wat NIET vergeten

- **`gws auth login` token verloopt vaak.** Bij gws-CalledProcessError
  in een dry-run-cost run: opnieuw inloggen met `gws auth login` en
  her-proberen.
- **`output/audit.db` houdt checkpoint.** Dry-runs zónder `--rehash`
  slaan bestaande (doc, clausule)-combinaties over. Voor een echte
  baseline-vergelijking altijd `--rehash` toevoegen.
- **`Ops_to_Biz/sessions/` is verwijderd** (commit `512c49a` op
  Ops_to_Biz). De `miro-kennissessie-generator` change is ook in
  iso-audit naar `openspec/changes/archive/` op de trim-branch.
- **Branch protection op `main`** is nog niet ingesteld (zie task
  §1.1.2). Mark moet dat zelf in GitHub UI doen wegens hook-
  classifier-restrictie.

## Memory-bestand zelf

Update dit document bij elke substantiële sessie:

- Verleg pointer "branch waar je werkt".
- Voeg nieuwe blocked-items toe onder "Wat NIET vergeten".
- Verwijder afgeronde items uit "Volgende sessie" en vervang door wat
  daarna komt.

Voor langetermijn-context (architectuur, missie, design-discipline):
zie `CLAUDE.md`, `docs/missie.md`, `ARCHITECTURE.md`.
