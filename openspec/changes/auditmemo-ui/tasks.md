# Tasks — auditmemo-ui

> API-first: de API is het duurzame product, de frontend wegwerpbaar. Dunne
> schil op de geteste motor (`landscape` / `run_audit` / `memo.draft` /
> `builder` / `renderer` / `sources`). Boring, lokaal-only. `/review` +
> `/security-review` vóór merge. Bevestig het stack-besluit (design.md).

## 0. Besluit & skeleton

- [ ] 0.1 Stack bevestigen (FastAPI) + dep via `uv add`; lokaal-only bind (127.0.0.1)
- [ ] 0.2 `iso-audit ui`/`serve`-command; bestand-gebaseerde sessie-working-dir

## 1. API — triage + memo (capability: audit-api)

- [ ] 1.1 `GET /findings` — findings + huidige classificatie + triage-status
- [ ] 1.2 `POST /findings/{id}` — reclassificeer (NC↔OFI) / zet triage-status, **append-only** in `decisions`/`classifications` (actor + timestamp + reden)
- [ ] 1.3 `POST /memo` — `draft` + render → HTML-preview + PDF (zelfde resultaat als `iso-audit memo`)
- [ ] 1.4 Tests: handlers met de motor gemockt; append-only-gedrag expliciet getest

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
