# Tasks — auditmemo-management

> Stack: Python 3.12, `uv`, pydantic v2, typer+rich, jinja2, weasyprint, PyYAML
> (`safe_load`). Max 200 regels per file. Interfaces in `protocols.py`.
> `/review` na elke task; `/security-review` na config-lezende tasks.

## 0. Voorbereiding

- [x] 0.1 Deps toevoegen via `uv add` (typer, rich, pydantic, jinja2, weasyprint); `uv.lock` gecommit. WeasyPrint systeem-libs (pango/cairo): aanwezig op dev-machine; nog documenteren in README (task 8.1)
- [x] 0.2 CLI-integratie-besluit: `memo`/`profile` als Typer-subapp achter de bestaande `iso-audit` console-script (akkoord Mark 2026-06-15)
- [x] 0.3 `iso_audit/memo/`-skeleton + `protocols.py` met `MemoRenderer`, `NormLookup`, `FindingsClassifier`, `ProfileLoader`, `PatternDetector`

## 1. Models & contracten

- [x] 1.1 `models.py`: pydantic v2 `Finding`, `HistoricalNC`, `MemoContext`, `ActionRow`, `NCBlock`, `ImprovementBlock`, `ClauseCitation`, `AuditMemo`
- [x] 1.2 Findings-input loader (`_laad_findings` in `cli.py`: JSON-lijst → `Finding`-models, duidelijke fout bij verkeerd type); gedekt door de integratietest

## 2. Norm-database (capability: norm-database)

- [x] 2.1 `norm_lookup.py`: `NormDatabase` laadt user-pointed directory met `<slug>.yaml`, `safe_load`, geen magische default
- [x] 2.2 Meertalige lookup (`title_<lang>`/`text_<lang>`); hard-fail bij ontbrekende clausule én ontbrekende taal-tekst. + 7 tests
- [x] 2.3 NL-voorbeeld-DB `examples/norms/iso-9001-2015.yaml` + `iso-27001-2022.yaml` (referentie-clausules, verbatim uit repo-normteksten; EN leeg = user-provided)
- [x] 2.4 Security-check: `safe_load` ✓, norm-DB-dir-resolutie weigert missende paden; bandit schoon op `memo/`

## 3. Profielsysteem (capability: memo-profiles)

- [x] 3.1 `theme/profile.py`: Profile-model + loader (XDG-slug + pad-traversal-guard), `schema_version`-check, kleurpalet met afgeleide defaults, hex-validatie, policy-gates → `ProfileError`. + 6 tests
- [x] 3.2 `theme/svg_validator.py`: weiger `<script>`/`<foreignObject>`/externe `<image>`/event-handler/javascript-URI/externe-entity. + 9 tests
- [x] 3.3 `theme/elicitation.py`: first-run wizard (8 stappen) met injecteerbare IO + `slugify`; vroege SVG-validatie. + tests
- [x] 3.4 `cli.py`: `profile new/list/show/validate`; `--profile <path>` via de loader-traversal-guard
- [x] 3.5 `examples/auditmemo/conduction.profile.yaml` + `minimal.example.yaml` (minimaal geldig profiel)
- [x] 3.6 Security-check: SVG-validator (script/foreignObject/externe-image/event-handler/javascript/entity geweigerd, getest), path-traversal-guards (`../etc/passwd`, `foo.bar`, `..` geweigerd), `safe_load`, geen eval/exec/subprocess. bandit schoon.

## 4. Classificatie & patronen (capability: auditmemo)

- [x] 4.1 `classifier.py`: `DefaultClassifier` — NC-extractie + verbeterpunt-promotie (expliciete flag + OFI-cluster-drempel, één representant/clausule). + tests
- [x] 4.2 `pattern_detection.py`: `DefaultPatternDetector` — cross-clause positief-vs-OFI-patroonzin met tellingen. + tests
- [x] 4.3 Verplichte classificatie-rationale bij verbeterpunt — verplicht veld op `ImprovementBlock`; template toont "Waarom verbeterpunt en geen NC?" (getest)

## 5. Rendering (capability: auditmemo)

- [x] 5.1 `templates/management-memo/`: `memo.html.j2` + partials (context, nc, improvement, historical) — print-CSS A4, palette-variabelen, inline SVG, `.placeholder`-styling (uit referentie-HTML)
- [x] 5.2 `renderer/html.py`: Jinja2-wrapper (autoescape, |safe op rich velden); injecteert profiel-palette + font-stack + logo
- [x] 5.3 `renderer/pdf.py`: WeasyPrint-wrapper; self-contained
- [x] 5.4 Action-table per NC (wat/wie/waar/uiterlijk) met gemarkeerde placeholders
- [x] 5.5 Voorbehoud-secties (auditscope + conditioneel onafhankelijkheid)
- [x] 5.6 Historical-NC-statustabel uit `historical_ncs.yaml`
- [x] 5.7 Audit-trail-metadata: HTML-comment met profile-slug/-versie, tool-versie, render-timestamp (injecteerbaar) en findings-hash — gestempeld in `build_memo`, gerenderd in het template (getest)

## 6. CLI memo-command (capability: auditmemo)

- [x] 6.1 `iso-audit memo --profile --findings --memo-input --norms --output [--historical-ncs --language --threshold]` schrijft HTML + PDF. Typer-subapp gewired achter de bestaande `iso-audit` console-script. + `profile list/show/validate`
- [x] 6.2 Heldere fouten bij ontbrekende/ongeldige inputs via `_fail` (ProfileError/ValueError/OSError → rode melding, exit 1; geen stille fallback)

## 7. Examples & integratietest

- [x] 7.1 `examples/auditmemo/`: `findings.json`, `memo-input.yaml`, `historical_ncs.yaml`, `conduction.profile.yaml` + `examples/norms/` (geanonimiseerd, reproduceert de referentie)
- [x] 7.2 Integratietest: render uit examples → HTML lxml-valid + PDF non-empty (5 tests)
- [x] 7.3 Norm-referentie-test: elke geciteerde clausule resolvet (NC 2 → 6.5/5.11/5.18); hard-fail bij ontbrekende
- [ ] 7.4 Handmatige structurele diff tegen referentie-PDF — structurele markers geverifieerd in de output; visuele diff door auditor (Mark)

## 8. Documentatie

- [x] 8.1 README-sectie "Management-auditmemo": memo- + profile-workflow
- [x] 8.2 `docs/memo-architecture.md`: lagen, ontwerpprincipes, uitbreidings-hooks-tabel, veiligheid
- [x] 8.3 `ONBOARDING.md` (mappentabel) + `CHANGELOG.md` bijgewerkt
- [x] 8.4 Bevestigd: alle `.py` in `memo/` ≤ 200 regels (max 153); templates gesplitst in partials
