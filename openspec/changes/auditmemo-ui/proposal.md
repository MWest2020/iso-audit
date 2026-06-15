## Why

De auditmemo-harness staat: landscape, run, LLM-draft (`iso-audit draft`) en
render (`iso-audit memo`) + profielen + user-pointed norm-DB + de triage-
checklist (`TriageStatus`). Maar de auditor werkt nu via JSON/YAML + CLI-flags.
De volledige auditor-flow is, van de grond:

1. **Landscape** bekijken — wat is gedekt, en wat niet (bv. geen Jira-bron).
2. **Run** zoals altijd (ingest → classificatie → output).
3. **Human-in-the-loop triage** — de auditor selecteert wat relevant is, pent
   NC↔OFI om, en zet de triage-status per kandidaat. Dit is de stap die nu
   ontbreekt en die de UI toevoegt.
4. **Auditmemo** voor management — het eindproduct.

Een **API-first kleine app** maakt deze flow bruikbaar: de **API is het
duurzame product**, de frontend is wegwerpbaar (minimale web/tkinter nu → later
een Nextcloud-app o.i.d.). Dit is de vastgelegde richting "harness = fundament,
UI = dunne schil" en sluit aan op de auditor-spiegel-capability.

## What Changes

- **HTTP-API** (lokaal) bovenop de bestaande motor, met endpoints per flow-stap:
  - `landscape` — coverage/gaps ophalen (welke bronnen/clausules wel/niet gedekt).
  - `run` — een run triggeren via een geregistreerde `source` (de connector-engine
    is de bestaande `iso_audit.sources`-registry).
  - `triage` — findings ophalen + per finding/kandidaat de classificatie
    (NC↔OFI) en triage-status muteren. **Append-only audit-trail.**
  - `memo` — `draft` + render naar HTML-preview + PDF-export.
- **Verwisselbare frontend**: een minimale web-UI die de API consumeert. Geen
  logica in de frontend; alle beslissingen lopen door de API zodat ze
  herleidbaar zijn. tkinter is een optie voor een snelle lokale spike, maar web
  deelt de HTTP-vorm met de Nextcloud-endgame.
- **Append-only triage**: reclassificatie en triage-keuzes worden in de
  bestaande `decisions`/`classifications`-tabellen vastgelegd (nooit
  overschrijven; wie/wanneer/waarom). De API dwingt dit af, niet de UI.

## Capabilities

### New Capabilities

- `audit-api` — lokale HTTP-API die de flow-stappen (landscape, run, triage,
  memo) blootlegt bovenop de bestaande motor; append-only voor beslissingen.
- `memo-ui` — minimale, verwisselbare frontend op de API voor de auditor-flow
  (triage + memo-review/render).
- `connector-orchestration` — een geregistreerde source via de API/UI triggeren
  tot een findings-dataset.

## Scope-grens

MVP: **lokale** API + minimale web-frontend voor stap 3 (triage) en 4 (memo),
met live HTML-preview + PDF-export. Stap 1 (landscape-view) en stap 2
(run-trigger) als opvolgende fasen. Buiten scope: multi-user/auth, hosting,
de Nextcloud-app zelf, een SPA-build, DB-migratie. Bewust boring en lokaal.
