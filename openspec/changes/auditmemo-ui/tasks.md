# Tasks — auditmemo-ui

> Dunne schil op de geteste harness (`memo.draft` / `builder` / `renderer` /
> `sources`). Boring & server-gerenderd; lokaal-only. `/review` + `/security-review`
> vóór merge. Bevestig eerst het stack-besluit (design.md "Niet opgelost").

## 0. Besluit & skeleton

- [ ] 0.1 Web-framework kiezen (FastAPI vs Flask) + dep toevoegen via `uv add`; bevestig lokaal-only bind
- [ ] 0.2 `iso-audit ui`-command (start server op 127.0.0.1); working-dir voor sessie-state

## 1. Review-workflow (capability: memo-ui)

- [ ] 1.1 Findings/draft laden in een sessie (bestand-gebaseerd, hervatbaar)
- [ ] 1.2 Kop-NC's tonen + per blok titel/afwijking/maatregel/acties redigeren (HTMX/vanilla)
- [ ] 1.3 Edits terugschrijven naar findings/memo-input (build_memo blijft enige assemblage-route)
- [ ] 1.4 Live HTML-preview + PDF-export-knop via de bestaande renderer
- [ ] 1.5 "Draft (her)genereren"-knop die `memo.draft.draft_findings` aanroept

## 2. Connector-orchestratie (capability: connector-orchestration, fase 2)

- [ ] 2.1 Source-keuze uit `sources.available()` in de UI
- [ ] 2.2 Ingest triggeren via de bestaande adapter → findings-dataset
- [ ] 2.3 Heldere fout bij ontbrekende credentials/config (geen stille fallback)

## 3. Kwaliteit & docs

- [ ] 3.1 Tests: route-/handler-tests met de motor gemockt; geen live LLM/credentials in CI
- [ ] 3.2 `/security-review`: lokaal-only bind, geen path-traversal via UI-inputs, YAML/SVG-guards blijven gelden
- [ ] 3.3 README + `docs/memo-architecture.md` bijwerken met de UI-workflow
- [ ] 3.4 Bevestig: handlers/modules ≤ 200 regels; UI is schil, geen gedupliceerde logica
