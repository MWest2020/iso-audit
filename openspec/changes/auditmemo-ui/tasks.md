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

- [ ] 2.1 Minimale web-pagina (Jinja2 + HTMX/vanilla): findings-lijst met triage-checklist + NC↔OFI-toggle
- [ ] 2.2 Memo-review: kop-NC's redigeren (titel/afwijking/maatregel/acties), live HTML-preview, PDF-export
- [ ] 2.3 Geen logica in de frontend — alles via de API (verwisselbaarheid bewijzen)

## 3. Flow-stappen 1 & 2 (fase 2)

- [ ] 3.1 `GET /landscape` — coverage/gaps (welke bronnen/clausules gedekt; bv. geen Jira)
- [ ] 3.2 `POST /run` — ingest via geregistreerde source (capability: connector-orchestration); heldere fout bij ontbrekende credentials/config
- [ ] 3.3 UI: landscape-view + run-trigger

## 4. Kwaliteit & docs

- [ ] 4.1 `/security-review`: lokaal-only bind, geen path-traversal via API-inputs, YAML/SVG-guards, append-only afgedwongen in de API
- [ ] 4.2 README + `docs/memo-architecture.md` bijwerken met de flow + API-contract
- [ ] 4.3 Bevestig: handlers/modules ≤ 200 regels; frontend is schil, geen gedupliceerde logica
