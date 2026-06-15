# Tasks — auditmemo-ui

> API-first: de API is het duurzame product, de frontend wegwerpbaar. Dunne
> schil op de geteste motor (`landscape` / `run_audit` / `memo.draft` /
> `builder` / `renderer` / `sources`). Boring, lokaal-only. `/review` +
> `/security-review` vóór merge. Bevestig het stack-besluit (design.md).

## 0. Besluit & skeleton

- [x] 0.1 Stack bevestigd (FastAPI + uvicorn + httpx via `uv add`); lokaal-only bind (127.0.0.1)
- [x] 0.2 `iso-audit ui`-command + `AuditSession` (bestand-gebaseerde working-dir met findings.json)

## 1. API — triage + memo (capability: audit-api)

- [x] 1.1 `GET /findings` — findings + classificatie + triage-status (FindingSummary)
- [x] 1.2 `POST /findings/{id}` — reclassificeer (NC↔OFI) / zet triage-status, **append-only** met actor + timestamp + reden. **Noot:** MVP schrijft naar een sessie-lokale `triage_log.jsonl` (append-only); integratie met de `decisions`/`classifications`-DB-tabellen is een follow-up
- [x] 1.3 `GET /memo/preview` (HTML) + `POST /memo/export` (PDF) via de bestaande motor
- [x] 1.4 Tests: TestClient — findings, reclassify NC→OFI append-only, trail groeit, 404, memo-preview (5 tests)

## 2. Frontend — triage + memo-review (capability: memo-ui)

- [x] 2.1 Web-pagina (`api/ui.html`, vanilla JS, geen build/deps): findings-lijst met NC↔OFI/POSITIVE-toggle (geen UNCLASSIFIED) + triage-select; severity-filter (NC-kandidaten / alle)
- [x] 2.1b Triage versimpeld naar `open`/`valide`/`niet_valide`; `niet_valide` valt uit de memo. **Memo-stap gated**: greyed-out + server-side 409 tot 0 openstaande NC-kandidaten (`GET /triage/status`)
- [x] 2.2 Memo-review: live HTML-preview (iframe) + PDF-export + **inline redactie** van kop-NC-tekst (titel/afwijking/maatregel) via `POST /findings/{id}` (append-only) + `GET /findings/{id}`. UI-editor in stap 4, gated met de memo-stap
- [x] 2.3 Geen logica in de frontend — alles via de API (severity/triage/preview/export)

## 3. Flow-stappen 1 & 2

- [x] 3.1 Stap 1 = **config-sectie**: `GET /config/options` (normen + bronnen) + UI-selectoren (geen feedback-dump meer)
- [x] 3.2 `POST /run/start` met **live-modus** (echte `run_audit`: Drive-ingest + LLM-classificatie, chapter-scoped, `no_review`) → DB-export → draft, met opgevangen "Stap X/7"-voortgang + logregels via `GET /run/progress`. **Sim-timer als fallback.** Bron-subscoping = nice-to-have (zie memory `todo-bron-subscoping`)
- [x] 3.3 UI: config-selectoren + run-knop

## 4. Kwaliteit & docs

- [ ] 4.1 `/security-review`: lokaal-only bind, geen path-traversal via API-inputs, YAML/SVG-guards, append-only afgedwongen in de API
- [ ] 4.2 README + `docs/memo-architecture.md` bijwerken met de flow + API-contract
- [ ] 4.3 Bevestig: handlers/modules ≤ 200 regels; frontend is schil, geen gedupliceerde logica
