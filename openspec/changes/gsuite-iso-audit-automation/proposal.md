## Why

Interne ISO 9001/27001 audits verlopen nu volledig handmatig: documenten lezen, bevindingen noteren, rapport schrijven. Dit kost veel tijd, is foutgevoelig en levert inconsistente rapportages op. Door de workflow te automatiseren via Claude Code + GSuite API wordt de auditcyclus reproduceerbaar, sneller en aantoonbaar normconform.

## What Changes

- Nieuw geautomatiseerd audit-systeem dat GSuite (Drive, Docs, Sheets, Slides, Gmail) én Miro integreert met Claude Code via MCP
- Documenten worden automatisch ingelezen uit Google Drive en gekoppeld aan norm-clausules (ISO 9001:2015 hfst 4-10 / ISO 27001:2022 Annex A)
- Notities, sticky notes en bevindingen worden ingelezen uit Miro-borden (auditorwerkruimte)
- Gecombineerd rapport: ISO 9001 + ISO 27001 in één document, met ISO 27001 Annex A als addendum
- Bevindingen worden geclassificeerd als NC / OFI / positief conform norm-eisen
- Rapporttemplate wordt aangemaakt als herbruikbaar Google Docs-document
- Gegenereerde output: auditrapport (Google Docs) + executive summary (Google Slides)
- Uitnodigingen via Google Calendar; optionele notificatie via Gmail

## Capabilities

### New Capabilities

- `audit-report-template`: Herbruikbaar Google Docs-template conform ISO 9001/27001 rapportage-eisen
- `document-ingestion`: Lezen en indexeren van procedures, werkinstructies en beleidsdocumenten uit Google Drive
- `clause-mapping`: Koppeling van documenten aan norm-clausules (ISO 9001 hfst 4-10 / ISO 27001 Annex A controls)
- `finding-classification`: Classificatie van bevindingen als NC, OFI of positief observatie
- `report-generation`: Automatisch vullen van het rapporttemplate op basis van bevindingen (Google Docs output)
- `slide-summary`: Genereren van executive summary als Google Slides presentatie
- `miro-ingestion`: Inlezen van notities, sticky notes en bevindingen uit Miro-borden als audit-input
- `notification-dispatch`: Uitnodigingen versturen via Google Calendar; optionele rapportnotificatie via Gmail

### Modified Capabilities

- (geen — dit is een volledig nieuwe integratie)

## Impact

- **Nieuwe dependencies**: GSuite MCP-server (Drive, Docs, Sheets, Slides, Gmail, Calendar), Miro MCP/API, Google Cloud service account met beperkte OAuth-scopes
- **Geen bestaande code geraakt**: dit is een zelfstandige nieuwe pipeline naast de ArgoCD-integratie
- **Secrets**: Google service account credentials beheerd via ESO/Vault, nooit in code of env vars
- **Taal**: alle output en rapportage in het Nederlands
- **Normen**: ISO 9001:2015 en ISO 27001:2022
