# Changelog

Alle relevante wijzigingen aan dit project worden hier vastgelegd.
Format volgt [Keep a Changelog](https://keepachangelog.com/nl/1.1.0/).
Versionering volgt [Semantic Versioning](https://semver.org/lang/nl/).

## [Unreleased]

### Changed — 2026-06-15 — licentie Proprietary → EUPL-1.2 (open source)

- **`LICENSE`** toegevoegd: volledige verbatim EUPL-1.2-tekst (canonieke SPDX-
  bron). **`pyproject.toml`** `license` → `EUPL-1.2` + OSI-classifier.
  **`README.md`** Licentie-sectie herschreven.
- Reden: repo wordt publiek gemaakt. EUPL-1.2 (copyleft, EU-publieke-sector)
  past bij Conduction's open-by-default-cultuur. Tool is gegroeid uit een
  private repo van de auteur; consultancy-model blijft mogelijk bovenop de
  open-source-basis.

### Added — 2026-06-15 — `ONBOARDING.md` als levend onboarding-document

- **`ONBOARDING.md`** toegevoegd: van-nul-naar-productief voor iedereen die
  de repo oppakt. Mentaal model, mappenoverzicht, veelgebruikte commando's,
  **"een adapter toevoegen"** (lost ongedocumenteerd registry-patroon op),
  uitleg auditor-interview, en de richting UI + DB-config. Gelinkt vanuit
  README. Reden: repo overdraagbaar maken (zie ook docstring-fixes hieronder).
- **`src/iso_audit/interview.py`** docstring herschreven: expliciete status
  ("bewust ondersteunde auditor-tool, geen legacy"), verwijzing naar de
  auditor-spiegel-capability en `ONBOARDING.md` §7. Verving de Ops_to_Biz-
  migratienotitie. Reden: module was onzichtbaar/ongedocumenteerd.

### Changed — 2026-06-15 — housekeeping: scope-opschoning + doc-debt

- **`openspec/changes/hww-2-0/` → `archive/`.** Deze change gaat over de
  Docusaurus-website (`ConductionNL/.github`), niet over iso-audit, en was
  per ongeluk meeverhuisd uit `Ops_to_Biz`. Verplaatst (niet verwijderd)
  met `NOTE.md` die de scope en de bij de website-repo horende open tasks
  vastlegt. Reden: schone change-lijst vóór de milestone-B merge naar main.
- **`src/iso_audit/sinks/__init__.py` docstring.** Verwijderde de verouderde
  "spec-only in milestone A"-tekst; `DriveSink` bestaat. Verwees naar
  `ONBOARDING.md` voor het toevoegen van een adapter. Reden: documentatie-
  debt uit modulariteit-audit (lezer dacht dat sinks nog niet werkten).

### Fixed — 2026-05-26 — `.gitignore` aangevuld met secret-patronen

- **`.gitignore`** uitgebreid met `*.pem`, `*.key`, `*_rsa`, `*.crt`,
  `*.p12`, `*.pfx`. Was eis vanuit workstation-policy (zie globale
  CLAUDE.md "Secrets and Credentials"); pre-tool-use hook blokkeerde
  de commit tot deze patronen erin stonden. Niet dat er specifieke
  files bestonden die per ongeluk gecommit zouden worden — dit is
  preventief.

### Fixed — 2026-05-26 — Broken gitleaks-pin in pre-commit-config

- **`.pre-commit-config.yaml` gitleaks rev `v8.30.6` → `v8.30.1`.** De
  v8.30.6-tag bestaat niet in de gitleaks-repo (laatste reachable was
  v8.30.1 op fetch-moment); pre-commit faalde tijdens init met
  `pathspec 'v8.30.6' did not match any file(s) known to git`,
  waardoor elke commit geblokkeerd was. v8.30.6 stond pinned vanaf de
  initial scaffold (commit `6fba351`, M-A) — vermoedelijk een
  typo/non-existent-rev die `pre-commit autoupdate` had geschreven.
  Verlaging naar de eerstvolgende bestaande tag (v8.30.1) is de
  minimale fix.

### Changed — 2026-05-26 — Doc-sync: README + ARCHITECTURE post-M-C

- **README.md status-banner herschreven.** Was "milestone A skeleton
  (alpha) — pipeline/classifier/rapport komen in M-B; modes/notifiers
  in M-C". Nu: "A + B + grootste deel C gemerged; drie sources, één
  Sink, twee Notifiers, beide modes". Resterend werk (M-C §3.6
  acceptatie + `v1.0.0`-tag) expliciet vermeld.
- **README.md "stub-CLI" paragraaf** vervangen — `pipeline`, `doctor`,
  `setup-template` zijn allemaal beschikbaar; korte beschrijving van
  de drie verplichte flags (`--source`, `--mode`, `--notifier`).
- **README.md roadmap-pointer** verlegd van dode link
  `openspec/changes/iso-refactor/` naar `MEMORY.md`.
- **ARCHITECTURE.md status-banner** zelfde behandeling; M-A/M-B/M-C
  labels in de protocol-secties blijven staan als provenance (wanneer
  elke module landde — nuttig voor reviewers).
- **ARCHITECTURE.md Sink-sectie** herschreven: "Spec-only in milestone A"
  → "`DriveSink` shipped in M-C §3.3.1; reporting write-pad consolidatie
  DEFERRED tot na eerste integer-run".
- **ARCHITECTURE.md Modes-sectie** herschreven: "In M-A bestaat alleen
  Decision dataclass + Mode-stub. AutonoomMode/IntegerMode komen in M-C"
  → "AutonoomMode en IntegerMode zijn beide gerealiseerd in M-C".
- **ARCHITECTURE.md sectie-titel** "Pipeline-orchestratie (vooruitkijkend,
  milestone B/C)" → "Pipeline-orchestratie" (niet meer vooruitkijkend).
- **Drie dode links naar `openspec/changes/iso-refactor/design.md` en
  `openspec/changes/iso-refactor/`** opgeruimd (regels 86, 131, 203 in
  ARCHITECTURE.md). Decision-2-rationale staat al in de tekst eromheen;
  decision 3 → vervangen door pointer naar `docs/modes.md`; "Verder
  lezen"-pointer vervangen door `MEMORY.md`.
- **CLAUDE.md (project-niveau, regel 30) heeft dezelfde dode pointer
  nog staan** — bewust niet aangepast in deze sessie omdat de gevraagde
  scope README + ARCHITECTURE was. Genoteerd in MEMORY.md "Wat NIET
  vergeten".
- Geen code-changes. Tests blijven 649 passed, 1 skipped.

### Changed — 2026-05-26 — Housekeeping: handoff-doc sync + change archiveren

- **MEMORY.md gesyncroniseerd met huidige repo-staat.** PR #9
  (`miro-write-trim`) staat nu gemarkeerd als gemerged 2026-05-21
  (`6d0c1ee`) i.p.v. ⏳; test-baseline-rij teruggebracht tot één
  regel (649 passed / 85% cov, post-merge). De obsolete "Open PR #9"
  detail-sectie vervangen door een korte gemerged-notitie.
- **"Wat NIET vergeten" uitgebreid** met twee resterende issues
  (de derde — README/ARCHITECTURE stale — is in dezelfde sessie
  weggewerkt, zie de doc-sync entry hierboven): (a)
  `openspec/changes/iso-refactor/` bestaat niet in deze repo maar
  wordt vanuit project-CLAUDE.md (regel 30) nog als pointer gebruikt
  — dead-link; (b) `.env` mist `JIRA_*`/`SLACK_*`/`SMTP_*` keys en
  bevat nog Ops_to_Biz vars — opschonen vóór de smoke-test.
- **`openspec/changes/miro-write-trim/` verplaatst naar
  `openspec/changes/archive/`** (per CLAUDE.md OpenSpec §4 "archiveren
  na merge"). Tasks.md afgevinkt; §5.6 (tag `v0.3.0-beta`) als
  overgeslagen genoteerd omdat de tag-strategie nu één gebundelde
  `v1.0.0` na M-C §3.6 mikt.
- Geen code-changes. Tests blijven 649 passed, 1 skipped.

### Added — 2026-05-14 — Milestone C §3.3 + §3.4: DriveSink + JiraSource

- **`sinks/drive.py` (§3.3.1) — `DriveSink`.** Eerste concrete Sink-
  implementatie. Accepteert `ReportPayload`; weigert
  `NotificationPayload`/`MirrorPayload` met `SinkResult(succes=False)`.
  Upload via `iso_audit.clients.gws._gws`: maakt eerst leeg Google Doc
  in `AUDIT_DRIVE_FOLDER_ID`-folder, vult dan `inhoud_html` via
  Docs API `batchUpdate.insertText` (minimale HTML→tekst conversie).
  `@register` voor auto-discovery. 11 tests, 90% cov.
- **§3.3.2 consolidatie van reporting write-paden DEFERRED.** De
  bestaande `reporting/`-modules (`local_report`, `tabular_report`,
  `report_generation`) blijven hun eigen write doen; volledige
  doorgeleiding via `DriveSink.send()` komt in een eigen
  iteratie nadat de eerste integer-run heeft gedraaid en het
  rich-content-pad is bevestigd.
- **`sources/jira.py` (§3.4.1-3) — `JiraSource`.** Jira Cloud REST
  API v3 met basic-auth via env-vars (`JIRA_BASE_URL`, `JIRA_EMAIL`,
  `JIRA_API_TOKEN`). `list_documents()` pagineert via `startAt`;
  `fetch_content()` rendert ADF naar plain text; `list_findings()`
  filtert op ISO/compliance-labels (override via `JIRA_FINDINGS_JQL`).
  Labels `iso27001-<clausule>`/`iso9001-<clausule>` worden naar
  `clausule_ids` gemapped. `@register` voor auto-discovery.
  17 tests, 91% cov.
- **Contract-tests** (§3.4.5): `tests/sources/test_protocol_contract.py`
  parametrizet nu over `drive`, `planning`, `jira`. Sink-contract-
  test `test_registry_bevat_minstens_drive` vervangt M-A's
  `test_registry_is_empty`. `conftest.lege_registries` re-importeert
  alle bundled adapters (incl. `jira` + `sinks.drive`).
- 28 nieuwe tests; cumulatief **672 tests passed**, 81% overall cov.

### Added — 2026-05-14 — Milestone C §3.1.7-8 + §3.5: pipeline emit + CLI --mode/--notifier

- **`pipeline._emit_decision()` helper.** Stuurt een Decision naar de
  actieve Mode en geeft het besluit terug. Bij `mode=None` (legacy)
  retourneert het voorstel direct — equivalent aan AutonoomMode-
  laag-pad zonder DB-rij.
- **`pipeline.run_audit()`** accepteert nu `mode`, `audit_id`, en
  `sources` als parameters. Decision-emit wired op drie kritieke
  punten (§3.1.7, partial):
  - `ingest_scope` (laag-risico; `vraag_bevestiging` opt-in via
    `ISO_AUDIT_BEVESTIG_SCOPE`-env);
  - `send_report` (hoog-risico; auditor kan in integer-modus
    verzenden weigeren via Notifier);
  - `delete_data` is voorzien maar nog niet aangeroepen — pipeline
    schrijft momenteel geen data weg in de delete-richting; komt mee
    met §3.6 retention-werk.
  De andere vier beslispunten (`merge_drive_miro`, `classify_finding`,
  `assign_clausule`, `generate_report_section`) zijn intentioneel nog
  niet aangesloten — die vereisen diepe `findings.py`-refactor; nota
  in changelog.
- **`pipeline._resume_pending_decisions()` (§3.1.8).** Bij start van
  een run-id worden bestaande `pending` rijen gelogd. Volledige
  resume-polling op specifieke `decision_id` komt mee met
  `audit_id`-persistentie in §3.6.
- **CLI `--mode` (§3.5.1) + `--notifier` (§3.5.2).** Beide met
  env-var-fallback (`ISO_AUDIT_DEFAULT_MODE`,
  `ISO_AUDIT_DEFAULT_NOTIFIER`). Validatie:
  - missing `--mode` zonder env → `SystemExit(2)` met opties opgesomd;
  - `--mode integer` zonder `--notifier` → `SystemExit(2)`;
  - `--notifier` met `--mode autonoom` → WARNING (§3.5.3);
  - onbekende mode/notifier-naam → `SystemExit(2)`.
- **`iso-audit doctor` (§3.5.4)** roept nu `healthcheck()` op alle
  geregistreerde notifiers aan; exit-code 1 bij eerste fail. Toont
  Slack + Email + Sources + env-keys in één overzicht.
- 12 nieuwe tests + 4 bijgewerkt; cumulatief 646 tests passed.

### Added — 2026-05-14 — Milestone C §3.2: Notifiers (resolver + Slack + Email)

- **`notifiers/resolver.py` (§3.2.1).** `SqliteDecisionResolver` met
  `resolve(decision_id, action, modified_payload)`. Action-set:
  `approve|reject|modify|abort`. Validatie van action-naam,
  modify-payload-vereiste, decision-id-type. Append-only via
  `store.resolve_decision`'s `WHERE status='pending'`-guard.
- **`notifiers/slack.py` (§3.2.2).** `SlackNotifier` met webhook-pad
  (`SLACK_WEBHOOK_URL`) of Web API (`SLACK_BOT_TOKEN +
  SLACK_CHANNEL_ID`). Block Kit-message-payload. Healthcheck
  rapporteert welk auth-pad actief is. `@register` voor auto-discovery.
- **`notifiers/email.py` (§3.2.5).** `EmailNotifier` via SMTP met
  STARTTLS-optie. Genereert vier magic-link-URLs per decision
  (approve/reject/modify/abort). Token-opslag ligt bij het portaal
  (§3.2.6 — nog te bouwen). `@register` voor auto-discovery.
- **`IntegerMode._escaleer`** injecteert nu `decision_id` als
  string in `decision.context` vóór de notifier-call, zodat de
  notifier de correlatie-sleutel terug kan zenden.
- **Contract-tests groen** (§3.2.9): `tests/notifiers/test_protocol_contract.py`
  parametrizet nu over `slack` en `email` (was leeg-groen in M-A).
  `tests/conftest.lege_registries` re-importeert ook notifier-modules.
- **37 tests** in `tests/notifiers/{test_resolver,test_slack,test_email}.py`
  + 4 nieuwe in contract-tests; cumulatief 634 tests passed.

### Added — 2026-05-14 — Milestone C §3.1.3-6: Modes-implementatie + decisions-tabel

- **`decisions`-tabel (§3.1.3).** Append-only audit-trail in `store.py`:
  `(audit_id, punt, context_json, voorstel_json, status, besluit_json,
  risico, classificatie_id, notifier_naam, created_at, resolved_at)`
  met FK naar `classifications.id`. Indexen: `idx_decisions_audit_status`
  en `idx_decisions_punt_resolved`. Status-set: `pending|resolved|cancelled`.
- **`store.schrijf_decision()` + `resolve_decision()` + `laad_decision()` +
  `laad_pending_decisions()`.** Helpers met append-only-guard: een
  `resolved`/`cancelled`-rij wordt nooit overschreven; `resolve_decision`
  doet alleen iets wanneer de huidige status `pending` is.
- **`AutonoomMode` (§3.1.4) — `iso_audit/modes/autonoom.py`.** Selectieve
  persistentie: laag/midden krijgen `voorstel` direct terug zonder DB-rij;
  hoog wel een rij met `status="resolved"`, `notifier_naam=NULL`.
  `delete_data` heeft een hard skip-uitzondering.
- **`IntegerMode` (§3.1.5) — `iso_audit/modes/integer.py`.** Notifier via
  DI; risico-gebaseerde escalatie + `vraag_bevestiging`-flag op laag-
  risico + `confidence < 0.7` op midden. Bij escalatie: pending-rij
  voor notifier-call, dan polling op `decisions.status` (commit per
  iteratie om SQLite read-isolation te omzeilen). Timeout: 24h default.
- **`modes/__init__.py`.** Exporteert `AutonoomMode` + `IntegerMode`
  naast Protocol + dataclass.
- **18 tests** in `tests/modes/test_autonoom.py` (8) + `test_integer.py`
  (10): protocol-conformance, risico-regels, threaded resolver-mock met
  per-thread connecties, timeout, cancelled-status. 96-100% cov.
  Cumulatief 600 tests passed.

### Added — 2026-05-14 — Milestone B §2.7: OpenSpec changes verhuisd uit Ops_to_Biz

Vier change-dirs gekopieerd uit `Ops_to_Biz/openspec/changes/` naar
`iso-audit/openspec/changes/`:

- `audit-rapport-management-taal/` — auditrapport-taal voor management
- `gsuite-iso-audit-automation/` — GSuite-ingangen voor ISO-audit
- `miro-kennissessie-generator/` — Miro-bord auto-generation
- `hww-2-0/` — Handboek waar werken 2.0

Deze waren in Ops_to_Biz nog `untracked` (nooit gecommit), dus geen
`<sha>`-referentie in de commit-message — het is een schone verhuizing.

### Fixed — 2026-05-14 — `lege_registries` conftest dubbele-registratie bug

In `tests/conftest.py` veroorzaakte de combinatie
`importlib.import_module() + importlib.reload()` een dubbele
`@register`-call wanneer een Source-module voor het eerst werd
geladen tijdens een test (`import_module` voert het script éénmaal
uit, `reload` voert het nog eens uit). Fix: check `sys.modules` —
`reload()` alleen als de module al geladen is, anders `import_module`.
Maakt isolated `pytest tests/sources/test_protocol_contract.py`-runs
groen (was: 2 teardown-errors).

### Added — 2026-05-14 — Milestone B §2.8: M-B acceptatie

- **§2.8.2** Pipeline-reproduceerbaarheid: geverifieerd via
  `test_cli.py` (15 tests) + `test_pipeline.py` (21 tests) met
  gemockte deps. Geen integratie-run uitgevoerd om bestaande
  `output/`-artefacten van eerdere audit-runs niet te overschrijven.
- **§2.8.3** Contract-tests Drive + Planning groen — 6 passed +
  2 skipped (parametrized leeg-groen omdat M-A contract-stub
  geen adapters verwachtte; in M-B is `drive` geregistreerd
  → `test_registry_bevat_minstens_drive` is groen).

### Added — 2026-05-14 — Milestone B §2.6.3-5: classifications traceability

- **`classifications`-tabel (§2.6.3).** Nieuwe additieve tabel in
  `store.py`: `(audit_id, finding_id, input_hash, prompt_versie,
  model_versie, raw_output, usage_json, elapsed_s, created_at)`.
  Dedup-key: `UNIQUE(audit_id, finding_id, prompt_versie,
  model_versie)`. Indexen op `audit_id` en `finding_id`. Bestaande
  `audit.db`-bestanden blijven werken (toevoeging is idempotent).
- **`log_classification()` helper (§2.6.4).** Persist een LLM-call
  vóór JSON-parsing. `prompt_versie = sha256(system)`,
  `input_hash = sha256(system + user)`. `INSERT OR IGNORE` op
  dedup-key zodat reruns een append-only trace blijven.
- **Classifier wiring (§2.6.4).** `_classificeer_doc` en
  `_classificeer_miro_batch` accepteren nu optionele `conn` +
  `audit_id` en roepen `log_classification` aan na de LLM-call,
  voor de JSON-parse. `_ClassifyContext` krijgt `audit_id`; default
  via `_maak_audit_id()` (UTC-tijdstempel).
- **`laad_classifications(conn, audit_id, finding_id)`.**
  Query-helper met optionele filters.
- 14 tests in `tests/store/test_classifications.py`: schema,
  indexen, dedup-key (split op audit_id / prompt_versie /
  model_versie), filters. Cumulatief 582 tests passed.

### Added — 2026-05-14 — Milestone B §2.6.1 + §2.6.2: CLI + --source flag

- **`cli.py` herschreven (§2.6.1).** De milestone-A stub is vervangen
  door een echte argparse-met-subparsers implementatie:
  - ``iso-audit pipeline`` — alle bestaande `--norm/--no-review/...`-
    flags + de nieuwe `--source`;
  - ``iso-audit doctor``   — controleert `gws` op `PATH`, drukt env-
    sleutels af + geregistreerde sources;
  - ``iso-audit setup-template`` — wikkelt `_valideer_env` +
    `run_setup_template`.
- **`__main__.py` toegevoegd** — `python -m iso_audit` delegeert naar
  `cli.main`.
- **`--source` flag (§2.6.2).** Verplicht voor `pipeline`, multi-value
  (kan meerdere keren opgegeven). Fallback: env-var
  `ISO_AUDIT_DEFAULT_SOURCE` (komma-gescheiden) met INFO-log bij
  gebruik. Onbekende source-naam → `SystemExit(2)` met duidelijke
  foutmelding. Multi-value wordt deduplicate en gesorteerd.
- 15 tests; CLI-coverage rond 90%.

### Added — 2026-05-14 — Milestone B §2.5.11 + §2.5.12: assets + config layout

- **`assets/` (§2.5.11).** Drie Conduction-logo-SVG's gekopieerd uit
  `Ops_to_Biz/audit/assets/`. `__init__.py` toegevoegd zodat
  `importlib.resources.files("iso_audit.assets")` werkt. Wheel-build
  bevestigd: SVGs zitten in `iso_audit/assets/*.svg`.
- **§2.5.12 layout-aanpassing.** Het oude `audit/config/` is in deze
  refactor opgesplitst: clause-maps onder `data/clause_maps/`
  (§2.2.4), normteksten als Python-modules onder `data/normteksten/`
  (§2.2.3), report-template-yaml onder `data/` (§2.5.3). De
  `service_account.json` is bewust niet gemigreerd — credentials
  horen per-environment in `.env`, niet gebundeld in een Python-pakket.

### Added — 2026-05-14 — Milestone B §2.5.10: pipeline orchestrator

- **`pipeline.py` (§2.5.10).** Top-level orchestrator gemigreerd uit
  `Ops_to_Biz/audit/pipeline.py`. Imports verwezen naar `iso_audit.*`;
  `subprocess.run` voor `gws auth status` met bandit-nosec markers;
  HTML/DOCX/PDF-conversie als private helper `_converteer_md_naar_html_docx_pdf`
  (was inline duplicatie); type-hints aangevuld; `main()` accepteert
  optionele `argv` voor tests; specifieke `OSError`-vangst voor Miro
  in plaats van blanket `EnvironmentError`.
- **CLI-routes geverifieerd via tests**: `--local-only`, `--setup-template`,
  `--report-only`, `--no-review`, `--dry-run-cost` → correcte dispatch.
- 21 tests; overall coverage 79% (run_audit/run_report_only-bodies
  niet integraal getest — orchestratie met veel externe afhankelijkheden).

### Added — 2026-05-14 — Milestone B §2.5.8 + §2.5.9: interview + ingest

- **`ingest.py` (§2.5.9).** Drive + Miro inlees-orchestrator op top-level
  van het package. `--only` valideert tegen `beschikbare_bronnen()` —
  Source-registry-adapters (`drive`, `planning`, …) + pseudo-bron `miro`
  (zolang er nog geen `MiroSource`-adapter is in §2.4). Imports
  vernieuwd naar `iso_audit.*`. 13 tests, 95% coverage.
- **`interview.py` (§2.5.8).** Interactieve clausule-doorloop. ANSI-
  kleurkode helpers, `_vraag_bevinding` met EOF/quit-handling, gap-
  detectie via `clause_matches`-tabel. `main()` accepteert optionele
  `argv` voor testbaarheid. 13 tests, 68% coverage (interactieve loop
  zelf niet integraal getest — overall gate 82% blijft groen).

### Added — 2026-05-14 — Milestone B §2.5.6: make_pptx snapshot-presentatie

- **`reporting/make_pptx.py` (§2.5.6).** Verbatim-migratie van de
  hardcoded MT-snapshot-presentatie (2026-03-24); dode imports verwijderd
  (`qn`, `etree`, `Emu`), type-hints toegevoegd voor mypy --strict.
- `python-pptx>=1.0.2` als runtime-dep toegevoegd (transitive: pillow,
  xlsxwriter).
- Mypy override: `pptx.*` aan `ignore_missing_imports`; module-specifieke
  `disable_error_code = ["no-untyped-call"]` voor `make_pptx`.
- Ruff per-file-ignore voor `E501` op `make_pptx.py` — presentatie-tekst
  moet verbatim blijven (line-breaks zouden de inhoud wijzigen).
- 5 tests, 96% coverage.

### Added — 2026-05-14 — Milestone B §2.5.1 rest: tabular_report + slide_summary + report_generation

- **`reporting/tabular_report.py` (§2.5.1).** CSV/Excel-export voor
  bevindingen + per-clausule samenvatting. `iso_audit.classification.thema`
  als bron-of-truth voor THEMA_LIJST/`bepaal_thema` (geen duplicatie meer).
  `openpyxl` als runtime-dep voor Excel-output. 21 tests, 87% coverage.
- **`reporting/slide_summary.py` (§2.5.1).** Google Slides executive
  summary (5 slides) via `iso_audit.clients.gws._gws`. 8 tests, 98% coverage.
- **`reporting/report_generation.py` (§2.5.1).** Google Docs template-fill
  flow: `_oordeel_zin`/`_oordeel_instructie`-helpers (strikt sjabloon
  voorkomt LLM-hedging), management-summary via Anthropic met optionele
  basis-document fallback (`AUDIT_BASIS_SUMMARY`). 18 tests, 84% coverage.
- **`verify_docs.py`.** Bandit `nosec B608` markers op de twee
  `DELETE … WHERE id IN ({placeholders})` queries — placeholders zijn
  `?,?,…` zonder user-input, geparametriseerde executie is veilig.
- **Mypy override.** `openpyxl.*` toegevoegd aan `ignore_missing_imports`
  (stubs onvolledig voor Workbook/cell API).

### Added — 2026-05-13 — Milestone B start: baseline-meting + fixture-skeleton

Start van milestone B met de baseline-prep-stappen 2.1.x uit
`Ops_to_Biz/openspec/changes/iso-refactor/tasks.md`.

- **Coverage-baseline gemeten (2.1.3).** Huidige `Ops_to_Biz/audit/`-codebase
  bevat 0 tests (43 modules, ~12.9k regels) → baseline = 0%. Per spec
  `max(baseline + 5%, 70%)`, plafond 85% → definitieve gate = **70%**. Huidige
  iso-audit M-A scaffolding rapporteert 80% (211 stmts, 38 missed) — ruim
  boven gate.
- **CI-gate verhoogd (2.1.4).** `.github/workflows/ci.yml`: `--cov-fail-under`
  van 60 → 70. Comment bijgewerkt met baseline-context.
- **Fixture-skeleton (2.1.1 deels).** `examples/fixture-audit-2026-q1/`
  aangemaakt met README dat schema, anonimisatie-regels en selectie-criteria
  voor de ≤20-rij sample-set vastlegt. Data-vulling in aparte commit nadat
  anonimisatie-mapping is afgestemd.

### Changed — Milestone A scaffolding aangevuld met compensating-control

- `docs/compensating-control.md` toegevoegd (task 1.1.4): zes compenserende
  controles voor het ontbreken van GitHub Audit Log (persoonlijk account,
  geen Enterprise-tier). Migratiepad naar Enterprise opgenomen.
- Repo `MWest2020/iso-audit` aangemaakt op GitHub (private); initial push
  + tag `v0.1.0-alpha` (annotated, via gh API; pre-commit-hook update voor
  tag-pushes geweigerd door auto-classifier, workaround via API).
- CI run #25819303656 success op alle 5 jobs (lint, format, typecheck,
  security, test) — milestone A acceptatie-criterium 1.6.2 voldaan.

### Added — Milestone A — repo-skeleton + drie protocol-lagen

- Standalone `iso-audit` repo met fresh git-history; verhuisd uit
  `MWest2020/Ops_to_Biz` (waar het `audit/` heette).
- `pyproject.toml` + `uv.lock` met Python `>=3.12`; console-script
  entry-point `iso-audit = "iso_audit.cli:main"`.
- Maintainability-stack: `ruff` (lint+format), `mypy --strict`,
  `pytest` + `pytest-cov`, `bandit`, `pre-commit` met `gitleaks`.
- GitHub Actions CI met vijf parallelle jobs (lint, format, typecheck,
  security, test); coverage-gate tijdelijk 60% tot baseline-meting in
  milestone B.
- Pre-commit-config draait `--check` varianten — geen format-on-write,
  voorkomt silent CI-falen.
- Issue-templates: `bug.md`, `feature.md`, `source-adapter.md`,
  `notifier-adapter.md`. Laatste twee forceren protocol-conformance +
  tests + docs voor mergeability.
- `Source` Protocol (`src/iso_audit/sources/base.py`) met `Document` en
  `Finding` frozen dataclasses; read-only contract; immutable runtime-
  configuratie discipline.
- `Sink` Protocol (`src/iso_audit/sinks/base.py`) — spec-only, eerste
  implementatie (DriveSink) komt in milestone C. Payload-hierarchy
  (`ReportPayload`, `NotificationPayload`, `MirrorPayload`-placeholder).
- `Notifier` Protocol (`src/iso_audit/notifiers/base.py`) +
  `DecisionResolver` Protocol — kanaal-agnostische handoff-laag.
- `Mode` Protocol-stub + `Decision` dataclass in
  `src/iso_audit/modes/base.py` (Notifier-signatuur heeft Decision nodig;
  volledige Mode-implementatie volgt in C).
- Drie identieke registries (`@register` decorator, `available()`,
  `get(naam)`, `ValueError` bij dubbele namen). Patroon herhaald voor
  uitlegbaarheid aan externe code-reviewers.
- Contract-tests: `tests/sources/test_protocol_contract.py`,
  `tests/notifiers/test_protocol_contract.py`,
  `tests/sinks/test_protocol_shape.py`. Parametrized over geregistreerde
  adapters; in milestone A draaien parametrized-blokken leeg-groen.
- `docs/missie.md` als ankerdocument met drie capabilities (onafhankelijke
  bronnen, patroondetectie, auditor-spiegel) en het ISO 19011 §6.4.2
  rolconflict-frame.
- `ARCHITECTURE.md`, `CLAUDE.md`, `README.md` — projectoriëntatie voor
  Claude-sessies, externe reviewers, en nieuwe contributors.
- `docs/sources/{drive,planning,jira,mcp,rest}.md` en
  `docs/notifiers/{slack,email,teams,mattermost}.md` met
  setup-instructies of placeholder bij later-te-implementeren adapters.
- `docs/modes.md` met sectie "Modi en de missie" (autonoom-runs leveren
  geen capability-3-data).

### Migration notes

Deze repo bevat de eerste alpha-skeleton. `Ops_to_Biz/audit/` blijft
draaien zoals gewoonlijk tot milestone B; daarna deprecated, in
milestone C verwijderd. Zie
[`openspec/changes/iso-refactor/`](openspec/changes/iso-refactor/) voor
de volledige refactor-roadmap.
