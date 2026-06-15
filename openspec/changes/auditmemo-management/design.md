# Design — auditmemo-management

## Referentie-artefact

De handmatige `Auditmemo_management_2026-05-06` (HTML = styling-bron-van-waarheid;
PDF = definitieve structuur) is leidend. Kernkenmerken die het eindproduct moet
reproduceren: A4 print-CSS (marge 18mm/20mm), Conduction-blauw `#4376fc`, inline
SVG-logo, cover → lead-summary → context → NC-blokken (met `norm-ref`, action-
table, dwingende taal) → verbeterpunt(en) → historical-NC-tabel → footer.
Placeholders zijn visueel gemarkeerd (`.placeholder`, italic + muted).

## Vastgelegde ontwerpbesluiten (geen elicitation nodig)

1. **Theme-systeem zonder Conduction-hardcoding.** Profielen zijn eerste-klas
   burgers; Conduction is één profiel. Profielen zijn **standalone overdraagbare
   YAML-bundles** — geen externe pad-refs, alleen wat in het profiel zelf staat.
2. **Inline SVG-logo** als string in het profiel (niet als pad) → self-contained
   PDF. Validator weigert SVG's met externe `<image>`, `<script>` of
   `<foreignObject>`.
3. **Kleurpalet per profiel**, niet één kleur: `primary` (verplicht), `accent`
   (default = primary), `muted`, `border`, `soft_bg`. Alle hex, alle gevalideerd.
   Sensible defaults afgeleid van `primary` → minimal-profile = primary + logo +
   org-naam.
4. **CSS-stack fonts**, geen vendored fonts / `@font-face`:
   `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`.
   Per profiel overschrijfbaar als stack-string.
5. **Profielen-locatie** `~/.config/iso-audit/profiles/<slug>.yaml` (XDG-conform);
   `--profile <path>` accepteert ook absolute paden voor ad-hoc/per-repo profielen.

## Long-term ontwerpconcepten (in de architectuur, niet in MVP-scope)

Deze zitten in de structuur zodat latere uitbreidingen geen breaking changes
vragen — maar worden in deze change niet geïmplementeerd:

- **Norm-database als plug-in.** Elk `<standard-slug>.yaml` in `data/norms/`
  (of opgegeven pad) wordt geladen. Voorbereid op 14001/22301/42001.
- **Memo-types als concept.** MVP: `management-memo`. Templates in
  `templates/<memo-type>/`. Toekomstige types (stakeholder-memo, externe-
  controle-reactiedocument) zonder refactor toevoegbaar.
- **Profile schema-versioning.** `schema_version: 1`; loader weigert onbekende
  versies met migratie-instructie.
- **Memo-output audit trail.** Onzichtbare HTML-comment + PDF-metadata met
  profile-slug/-versie, tool-versie, render-timestamp, findings-dataset-hash →
  elke memo herleidbaar naar zijn bron-inputs.
- **Talen als data, niet als code.** Norm-tekst, UI-strings, template-strings in
  YAML/JSON. MVP: NL + EN; nieuwe taal zonder code-wijziging.
- **Historical NCs als cross-audit register.** `historical_ncs.yaml` is een
  doorlopend document; elke cyclus voegt entries toe / werkt status bij.

## Stack & standards

- Python 3.12+, `uv` exclusief. `pydantic` v2 (models), `typer` + `rich` (CLI),
  `jinja2` (HTML-templating), `weasyprint` (PDF), `PyYAML` met **`safe_load`**.
- **Max 200 regels per file** (templates mogen langer; splits in partials).
- **Interfaces in `protocols.py`:** `MemoRenderer`, `NormLookup`,
  `FindingsClassifier`, `ProfileLoader`, `PatternDetector`.
- Boring & auditable: geen magic, geen impliciete defaults; bij ontbrekende data
  **harde fout met heldere melding**, geen stille fallback.

> **Afhankelijkheden-noot:** `typer`, `rich`, `pydantic`, `jinja2`, `weasyprint`
> zijn nieuwe deps. WeasyPrint heeft systeem-libs nodig (pango/cairo). Toevoegen
> via `uv add` met respect voor `uv.lock` (`uv sync --frozen` in CI). Bestaande
> CLI gebruikt `argparse`; de memo-CLI gebruikt Typer als zelfstandige sub-app —
> integratie met het bestaande `iso-audit`-entrypoint wordt in tasks.md belegd.

## Architectuur

```
iso_audit/memo/
├── cli.py                  # `iso-audit memo` + `profile` subcommands (Typer)
├── protocols.py            # MemoRenderer, NormLookup, FindingsClassifier, ProfileLoader, PatternDetector
├── models.py               # pydantic v2 models (Finding, MemoContext, ...)
├── classifier.py           # NC- + verbeterpunt-extractie
├── pattern_detection.py    # cross-clause patronen
├── norm_lookup.py          # YAML-backed norm-tekst lookup
├── theme/
│   ├── profile.py          # Profile-model + loader
│   ├── elicitation.py      # first-run wizard
│   └── svg_validator.py    # inline-SVG safety check
├── renderer/
│   ├── html.py             # Jinja2 wrapper
│   └── pdf.py              # WeasyPrint wrapper
├── templates/management-memo/{memo.html.j2, partials/...}
└── data/norms/{iso-9001-2015.yaml, iso-27001-2022.yaml}
    data/profiles/conduction.example.yaml
```

## Schema's (samengevat)

- **Profile** (`schema_version: 1`): `slug`, `organization{name,legal_form}`,
  `auditor{name,role}`, `brand{logo_svg, colors{primary,...}, font_stack}`,
  `standards[]`, `defaults{language, include_independence_caveat}`.
- **Finding** (pydantic): `id`, `severity` ∈ {NC,OFI,POSITIVE,UNCLASSIFIED},
  `standard`, `clause`, `title`, `description`, `evidence[]`,
  `source_memo?`, `promote_to_improvement=False`.
- **MemoContext** (pydantic): `audit_cycle` (vrije tekst), `scope` (per norm:
  geauditeerde hoofdstukken), `sources[]` (geraadpleegde bronnen), `dataset_counts`
  (totaal + per severity, afgeleid uit findings), `scope_caveat`,
  `independence_caveat?` (conditioneel), `discussion` (datum + met wie, optioneel).
- **NC-blok-aggregatie:** een NC-blok is niet 1:1 met één clausule. Eén NC kan
  **meerdere clausules citeren** (NC 2: §6.5/§5.11/§5.18) en **meerdere
  evidence-items** met eigen clausule-annotatie bevatten (NC 1 bundelt vijf
  memo's). Het model voorziet daarom een primaire clausule voor de heading plus
  een lijst geciteerde clausules en verrijkte evidence.
- **Norm-DB**: `metadata{standard,slug,source}`, `clauses{<id>{title_nl,
  title_en,text_nl,text_en}}`. Ontbrekende clausule → harde fout.
- **Historical NCs** (`schema_version: 1`): `entries[]{id, source_audit,
  source_document, finding_summary, status ∈ {open,in_progress,closed},
  closed_date?, closed_evidence?}`.

## Validation gates

- `/review` na elke task (incl. 200-regel-limiet). `/security-review` na
  config-lezende tasks: `safe_load`, geen path-traversal in `--profile <path>`,
  SVG-validator, geen `eval`/`exec`/`subprocess` zonder absoluut pad.
- Integratie: render uit `examples/` (findings + historical_ncs + profile);
  HTML lxml-valid; PDF zonder WeasyPrint-warnings; structureel equivalent aan het
  referentie-PDF (handmatig, niet pixel-exact).
- Norm-referenties: elke `clause` in een NC moet resolven; CI faalt anders.

## Niet opgelost / aandachtspunten

- **CLI-integratie argparse ↔ Typer.** Het bestaande `iso-audit`-entrypoint is
  argparse-gebaseerd. Optie: Typer-subapp mounten of `memo` als losse Typer-app
  achter dezelfde console-script. Te beslissen in implementatie (task 1).
- **MVP-clausuledekking** beperkt tot de set uit het referentievoorbeeld; volledige
  normtekst is een latere change.
