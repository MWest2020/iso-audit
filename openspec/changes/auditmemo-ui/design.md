# Design — auditmemo-ui

## Uitgangspunt

De UI is een **dunne schil** op een geteste harness. Niets van de memo-logica
wordt opnieuw geïmplementeerd: de UI roept `iso_audit.memo.draft.draft_findings`,
`builder.build_memo`, `renderer` en de `iso_audit.sources`-registry aan. Bouw de
UI dus pas nu de motor af is (gedaan in `auditmemo-management`).

## Stack-besluit (te bevestigen vóór implementatie)

Voorstel: **boring & server-gerenderd**, geen SPA-build.

- **FastAPI** (of Flask) als lokale server; start via `iso-audit ui`.
- **Jinja2** (al een dep) voor server-rendered pagina's; **HTMX** of vanilla JS
  voor de edit-interacties (geen build-step, geen npm-toolchain).
- **WeasyPrint** (al een dep) voor de PDF-export-knop.
- Bind standaard op **127.0.0.1** (lokaal, single-user). Geen auth in de MVP —
  maar expliciet gedocumenteerd als lokaal-only; geen externe expositie.

Reden: past bij "boring, auditable", vermijdt een frontend-build/supply-chain,
hergebruikt bestaande deps. Een SPA is uit scope.

## Datastroom

```
[source-registry] --ingest--> findings.json
       │ (fase 2, via UI)
findings.json --draft--> draft (LLM kop-NC's)  ──► review-UI (edit titel/
                                                    afwijking/maatregel/acties)
       review-UI --opslaan--> findings + memo-input  ──► build_memo ──► HTML-preview / PDF
```

De edits in de UI muteren de **findings/memo-input** (de bron), niet het
render-model — zo blijft `build_memo` de enige assemblage-route en blijft de
audit-trail (findings-hash, timestamp) kloppen.

## Niet opgelost / aandachtspunten

- **Web-framework-keuze** (FastAPI vs Flask) + nieuwe dep — bevestigen vóór bouw.
- **State**: waar leeft de sessie-staat (in-memory vs een working-dir met
  findings/draft-bestanden)? Voorstel: bestand-gebaseerd in een working-dir, zodat
  een sessie reproduceerbaar/hervatbaar is en near-idempotent blijft.
- **Security**: lokaal-only bind; SVG/YAML-guards van de harness blijven gelden;
  geen path-traversal via UI-inputs. `/security-review` vóór merge.
- **Connector-trigger** raakt live credentials (gws/Jira) — fase 2, met dezelfde
  expliciete-config-discipline als de CLI.
