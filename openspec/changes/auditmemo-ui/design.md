# Design — auditmemo-ui

## Uitgangspunt: API-first, verwisselbare frontend

De **API is het duurzame product**; de frontend is wegwerpbaar. De UI roept de
bestaande motor aan — `reporting/landscape`, `run_audit`, `memo.draft`,
`builder`/`renderer`, de `iso_audit.sources`-registry — en herimplementeert
niets. Zo kan de eerste frontend (minimale web of tkinter) later vervangen
worden door bv. een Nextcloud-app die dezelfde API consumeert.

Advies: eerste frontend een **minimale web-pagina** (deelt de HTTP-contract-vorm
met de Nextcloud-endgame), niet tkinter (desktop-only, deelt niets visueel).
tkinter blijft een optie voor een snelle lokale spike.

## Stack-besluit (te bevestigen vóór implementatie)

- **FastAPI** als lokale API (auto-OpenAPI-schema = nuttig contract voor latere
  clients). Start via `iso-audit ui`/`serve`. Bind op **127.0.0.1**.
- Frontend: server-rendered **Jinja2** (al een dep) + **HTMX**/vanilla JS, geen
  SPA-build / npm-toolchain.
- **WeasyPrint** (al een dep) voor PDF-export.
- Geen auth in de MVP — expliciet lokaal-only gedocumenteerd.

## De flow als API-endpoints

```
1. GET  /landscape        → coverage/gaps (welke bronnen/clausules gedekt; bv. geen Jira)
2. POST /run              → trigger ingest via een geregistreerde source → findings
3. GET  /findings         → findings + huidige classificatie + triage-status
   POST /findings/{id}    → reclassificeer (NC↔OFI) / zet triage-status  [APPEND-ONLY]
4. POST /memo             → draft (LLM) + render → HTML-preview + PDF
```

## Append-only triage (27001-scope, non-negotiable)

Stap-3-acties zijn auditor-**beslissingen**. De API MUST ze append-only
vastleggen in de bestaande `decisions`/`classifications`-tabellen: nooit
overschrijven, elke override met actor + timestamp + reden. De gerenderde memo
verwijst naar deze trail (samen met de findings-hash) → volledig herleidbaar.
De UI toont de huidige staat; de **API** bewaakt de onveranderlijkheid.

## Datastroom

```
[landscape] → [source-registry: ingest] → findings (DB)
   → triage-UI (reclassify/selecteer, append-only) → findings + memo-input
   → draft (LLM kandidaten + triage-checklist) → build_memo → HTML-preview / PDF
```

Edits muteren findings/memo-input + de append-only trail; `build_memo` blijft de
enige assemblage-route zodat de audit-trail klopt.

## Niet opgelost / aandachtspunten

- **Framework + nieuwe dep** (FastAPI) bevestigen vóór bouw.
- **Sessie-state**: bestand-gebaseerd in een working-dir (reproduceerbaar,
  hervatbaar, near-idempotent) i.p.v. in-memory.
- **Security**: lokaal-only bind; YAML/SVG/path-guards van de harness blijven
  gelden; geen path-traversal via API-inputs. `/security-review` vóór merge.
- **Connector-trigger** raakt live credentials (gws/Jira) — fasering met dezelfde
  expliciete-config-discipline als de CLI.
- **Fasering**: MVP = stap 3 (triage) + 4 (memo). Stap 1 (landscape-view) en 2
  (run-trigger) erna.
