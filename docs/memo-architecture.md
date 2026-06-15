# Auditmemo-architectuur

De `iso-audit memo`-feature genereert de **management-auditmemo** (HTML + PDF)
uit de findings-dataset. Dit document beschrijft de architectuur en de
**uitbreidings-hooks** zodat een opvolger (of consultancy-klant) kan uitbreiden
zonder breaking changes. Zie ook `openspec/changes/auditmemo-management/`.

## Lagen

```
findings.json ─┐
memo-input.yaml├─► builder.build_memo ─► AuditMemo ─► renderer ─► HTML + PDF
historical.yaml┘        ▲   ▲   ▲
profiel (YAML) ─────────┘   │   └── norm_lookup (user-pointed norm-DB)
                  classifier + pattern_detection
```

- **`models.py`** — pydantic v2: `Finding`, `HistoricalNC`, `MemoInput`
  (input) en `NCBlock`/`ImprovementBlock`/`MemoContext`/`AuditMemo` (render).
- **`classifier.py`** — selecteert NC's en verbeterpunten (expliciete promotie
  of OFI-cluster-drempel). Deterministisch, geen LLM.
- **`pattern_detection.py`** — cross-clause patroonzin (positief vs OFI).
- **`norm_lookup.py`** — laadt een **user-pointed** norm-DB-directory; hard-fail
  bij ontbrekende clausule/taal.
- **`theme/`** — profielsysteem (model, loader, SVG-validator, wizard).
- **`renderer/`** — Jinja2 (`html.py`) → WeasyPrint (`pdf.py`).
- **`builder.py`** — bindt alles samen + stempelt audit-trail-metadata.
- **`cli.py`** — Typer-subapp achter de `iso-audit` console-script.
- **`protocols.py`** — `NormLookup`, `FindingsClassifier`, `PatternDetector`,
  `ProfileLoader`, `MemoRenderer` — vervang elke laag los.

## Ontwerpprincipes

- **Multi-tenant via profielen.** Conduction is één profiel; elke klant krijgt
  een eigen standalone YAML-bundle (inline SVG-logo, kleurpalet met afgeleide
  defaults, CSS-stack-font). Geen Conduction-hardcoding.
- **Norm-DB user-pointed, repo lean.** De clausuleteksten zitten niet in de
  repo; de gebruiker wijst een norm-DB-directory aan. De repo ship slechts een
  NL-voorbeeld (`examples/norms/`). Een memo bevat **nooit** een verzonnen
  norm-citaat — ontbrekende clausule/taal = harde fout.
- **Self-contained output.** Inline SVG + CSS-stack-font → geen externe assets.
- **Near-idempotent + auditeerbaar.** `build_memo(now=...)` is injecteerbaar;
  de audit-trail-comment (profiel-slug/-versie, tool-versie, timestamp,
  findings-hash) maakt elke memo herleidbaar naar zijn bron.

## Uitbreidings-hooks (latere changes)

| Wil je… | Doe dit |
|---|---|
| Een nieuwe **norm-standaard** (14001/22301/42001) | Voeg `<slug>.yaml` toe aan de norm-DB-directory. Geen code. |
| Een **taal** toevoegen | Vul `title_<lang>`/`text_<lang>` in de norm-DB + render met `--language`. Template-strings zijn data. |
| Een **nieuw memo-type** (stakeholder-memo, externe-controle-reactie) | Nieuwe map `templates/<memo-type>/`; hergebruik builder/renderer-lagen. |
| Een **klantprofiel** | `iso-audit profile new` (wizard) of een YAML-bundle; `--profile <pad>`. |
| Profiel-**schema migreren** | Verhoog `schema_version`; de loader weigert onbekende versies met instructie. |

## Veiligheid

- Profiel-YAML + norm-YAML via `yaml.safe_load`.
- `--profile <pad>` / norm-DB-pad: geen path-traversal buiten toegestane scope;
  slugs zijn `[a-z0-9_-]`.
- SVG-validator weigert `<script>`, `<foreignObject>`, externe `<image>`,
  event-handlers, `javascript:`-URI's en externe entities.
- Jinja2 met autoescape; alleen auditor-gecontroleerde rich velden + het logo
  gebruiken `|safe`.

## Werken eraan

```
uv run iso-audit memo --profile examples/auditmemo/conduction.profile.yaml \
  --findings examples/auditmemo/findings.json \
  --memo-input examples/auditmemo/memo-input.yaml \
  --historical-ncs examples/auditmemo/historical_ncs.yaml \
  --norms examples/norms --output output/memo
uv run pytest tests/memo/
```
