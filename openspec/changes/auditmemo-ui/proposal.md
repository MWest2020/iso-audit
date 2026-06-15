## Why

De auditmemo-harness staat: `iso-audit draft` (LLM-draft van kop-NC's uit een
ruwe run) + `iso-audit memo` (render naar HTML/PDF) + profielen + user-pointed
norm-DB. Maar de auditor werkt nu via JSON/YAML-bestanden en CLI-flags — niet
toegankelijk. Het eindproduct (de management-memo) is auditor-oordeelswerk:
welke NC's de kop-NC's worden, het narratief, de maatregelen, de acties.

Een **auditor-UI** maakt die review-loop bruikbaar: findings inzien, de
LLM-draft per kop-NC reviewen/redigeren, en de memo renderen — zonder een
editor op een YAML-bestand. Dit is de volgende stap in de vastgelegde richting
"harness = fundament, UI erop, auditor houdt het oordeel" en sluit aan op de
auditor-spiegel-capability.

Daarbovenop: de **connector-engine** (de bestaande `iso_audit.sources`-registry:
Drive/Planning/Jira) via de UI laten triggeren, zodat de hele keten —
ingest → classificatie → findings → LLM-draft → review → memo — vanuit één
plek loopt.

## What Changes

- **Nieuwe `iso-audit ui` (of `serve`) command**: start een **lokale** web-UI
  (single-user, geen externe expositie) bovenop de bestaande harness.
- **Review-workflow**: laad een findings-dataset (of draft), toon de
  gedrafte kop-NC's, laat per blok titel/afwijking/maatregel/acties redigeren,
  render live naar HTML-preview + PDF-export. Edits gaan terug naar de
  findings/memo-input — de motor (`build_memo`/`render`) blijft de bron.
- **Connector-orchestratie (gefaseerd)**: kies een geregistreerde `source`,
  trigger ingest → findings, en stroom door naar de draft/review. De
  sources-registry is de connector-engine; de UI is de trigger-schil.
- **Geen herimplementatie van logica in de UI**: de UI roept de bestaande
  `draft`/`builder`/`renderer`/`sources`-lagen aan (dunne schil).

## Capabilities

### New Capabilities

- `memo-ui` — lokale auditor-UI voor review/edit/render van de management-memo
  bovenop de bestaande draft/render-motor.
- `connector-orchestration` — een geregistreerde source via de UI triggeren tot
  een findings-dataset, als opstap naar draft → review → memo.

## Scope-grens

MVP: **lokale** review-UI over een bestaande findings/draft, met live
HTML-preview + PDF-export. Connector-trigger als tweede fase. Buiten scope:
multi-user/auth, hosting/deployment, gelijktijdige sessies, een SPA-build —
bewust een boring, server-gerenderde aanpak (zie design).
