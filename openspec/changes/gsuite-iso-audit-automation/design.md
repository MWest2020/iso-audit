## Context

De huidige auditworkflow is volledig handmatig: een auditor leest documenten uit Google Drive, noteert bevindingen in een teksteditor of spreadsheet, en schrijft vervolgens een rapport conform ISO 9001 of ISO 27001 vereisten. Dit proces duurt meerdere dagen, is niet reproduceerbaar en levert wisselende rapportkwaliteit op.

De nieuwe pipeline automatiseert dit via Claude Code als orchestrator, aangestuurd via GSuite MCP-koppelingen. De auditor blijft in de loop voor menselijk oordeel, maar het systeem levert kant-en-klare concepten.

**Stakeholders**: interne auditors, ISO-coördinator, management (ontvangt executive summary)

**Constraints**:
- GSuite MCP-server moet beschikbaar zijn met Drive/Docs/Sheets/Slides/Gmail scopes
- Google service account credentials nooit in code — beheerd via Vault/ESO
- Output volledig in het Nederlands
- Normen: ISO 9001:2015 en ISO 27001:2022

## Goals / Non-Goals

**Goals:**
- Automatisch inlezen van Drive-documenten en koppelen aan norm-clausules
- Classificeren van bevindingen (NC / OFI / positief) via Claude
- Genereren van een volledig auditrapport in Google Docs op basis van een herbruikbaar template
- Genereren van een executive summary in Google Slides
- Optionele verzending via Gmail

**Non-Goals:**
- Real-time monitoring van documentwijzigingen (geen webhook/trigger pipeline)
- Externe certificatie-indieninfrastructuur
- Integratie met Jira/Linear voor actiepuntenopvolging (toekomstige iteratie)
- Automatische planningskoppeling via Google Calendar (optioneel, later)

## Decisions

### D1: Claude Code als orchestrator, niet als microservice
**Keuze**: De pipeline draait als een Claude Code-sessie met MCP-tools, niet als een aparte applicatieserver.
**Rationale**: Past in het bestaande Ops-to-Biz-patroon (zie ArgoCD-integratie), geen extra infra nodig, auditor kan de flow interactief bijsturen.
**Alternatief overwogen**: FastAPI-service met achtergrondtaken — te veel overhead voor een periodieke auditcyclus.

### D2: Gelaagde pipeline in vijf fasen
**Keuze**: De flow volgt de vijf stappen uit de prompt (template → ingest → valideer → rapporteer → presenteer) als afzonderlijke, aanroepbare fasen.
**Rationale**: Elke fase is testbaar en kan los worden herhaald zonder de volledige pipeline opnieuw te draaien. De auditor kan na validatiefase handmatig corrigeren voor rapportage.
**Alternatief overwogen**: Monolithische one-shot pipeline — te weinig controle voor menselijke review.

### D3: Google Docs template als single source of truth voor rapportstructuur
**Keuze**: Het rapporttemplate wordt opgeslagen als een echte Google Docs-bestand in Drive, met named placeholders (`{{management_summary}}`, `{{bevindingen_nc}}`, etc.).
**Rationale**: Template is herbruikbaar, aanpasbaar door auditors zonder code-wijzigingen, en blijft in het bekende GSuite-ecosysteem.
**Alternatief overwogen**: Jinja2-HTML template lokaal renderen → export naar PDF — vereist extra rendering stack, verlies van Drive-toegankelijkheid.

### D4: Norm-clausule mapping als configuratiebestand (YAML)
**Keuze**: De koppeling tussen norm-clausules en zoektermen/documenttypen wordt beheerd in een `clause_map.yaml` per norm (9001, 27001).
**Rationale**: Auditors kunnen de mapping aanpassen zonder code te wijzigen. Versiebeheerd in git.
**Alternatief overwogen**: Hardcoded in Python — niet onderhoudbaar bij normherzieningen.

### D5: Gecombineerd ISO 9001 + 27001 rapport met addendum-structuur
**Keuze**: Het rapport heeft één hoofdstructuur (ISO 9001 als basis), met een apart addendum-hoofdstuk voor ISO 27001 Annex A controls.
**Rationale**: Gecombineerd rapport vermindert administratieve overhead; het addendum maakt duidelijk welke bevindingen exclusief 27001-specifiek zijn.
**Alternatief overwogen**: Twee losse rapporten — dubbel werk, moeilijker te consolideren voor management.

### D6: Miro als secundaire input-bron naast Drive
**Keuze**: Miro-borden worden ingelezen als aanvullende input (auditornotities, sticky notes), niet als primaire documentbron. Drive-documenten blijven leading voor clausule-dekking.
**Rationale**: Miro wordt gebruikt als werkruimte tijdens audits; notities daar zijn waardevolle pre-bevindingen die anders verloren gaan.
**Alternatief overwogen**: Miro-notities handmatig overtypen naar Sheets — foutgevoelig en tijdrovend.

### D7: Secrets via .env (nu) → Vault/ESO (later)
**Keuze**: Secrets (GSuite service account JSON pad, Miro API token) worden tijdelijk beheerd via een `.env`-bestand. `.env` staat in `.gitignore` en wordt nooit gecommit. Migratie naar Vault/ESO volgt zodra die infrastructuur beschikbaar is.
**Rationale**: Vault/ESO is nog niet ingericht. `.env` is de veiligste lokale optie zolang secrets uit code en git blijven.
**Risico**: `.env` biedt geen audit trail, rotatie-mechanisme of toegangscontrole. Acceptabel voor lokale ontwikkeling; niet voor productie.
**Migratie**: bij Vault/ESO-beschikbaarheid — vervang `.env`-referenties door ESO SecretStore zonder code-wijzigingen (alleen configuratie).
**Alternatief overwogen**: hardcoded in code — uitgesloten.

### D8: Calendar voor planningskoppeling, Gmail als notificatie-fallback
**Keuze**: Audit-uitnodigingen en planningsbeheer lopen via Google Calendar MCP. Gmail wordt enkel gebruikt voor ad-hoc rapportnotificaties.
**Rationale**: Calendar is de juiste tool voor terugkerende auditcycli en biedt RSVP-tracking. Gmail-notificaties zijn bijzaak.
**Alternatief overwogen**: Alles via Gmail — geen planningsbeheer, geen RSVP.

## Risks / Trade-offs

| Risico | Mitigatie |
|--------|-----------|
| GSuite MCP-server mist of heeft onvoldoende scopes | Documenteer vereiste OAuth-scopes expliciet in README; voeg scope-validatie toe aan opstartcheck |
| Claude classificeert een bevinding incorrect (NC vs OFI) | Validatiefase toont alle classificaties ter menselijke review vóór rapport wordt gegenereerd |
| Drive-documenten zonder structuur (scans, afbeeldingen) | Detecteer niet-tekstuele bestanden en flag ze als "vereist handmatige review" |
| Template raakt out-of-sync met normvereisten | Template-versie en normdatum opnemen in metadata; jaarlijkse review als taak in tasks.md |
| Rate limits GSuite API bij grote documentsets | Implementeer retry-with-backoff; verwerk documenten in batches van max 20 |

## Open Questions

*(Beantwoord 2026-03-13)*

- ~~Drive-mappenstructuur~~: Één gedeelde Drive gekoppeld aan het account van de auditor. Bestaande auditrapportages staan onder map "Interne Audits".
- ~~Bestaand auditrapport~~: Ja, aanwezig in Drive onder "Interne Audits" — wordt gebruikt als basis voor template-analyse (stap 2.1 in tasks).
- ~~Gecombineerd rapport~~: Ja — ISO 9001 en ISO 27001 in één document. ISO 27001 Annex A controls vormen een addendum, niet een apart rapport.
- ~~Gmail-ontvangers~~: Gmail primair voor uitnodigingen; planningskoppeling via Google Calendar. Directe rapportnotificatie via Gmail optioneel.

**Nog open**:
- Miro API token — nodig tijdens implementatie, beheerd via Vault/ESO.

**Gesloten**:
- Miro board-ID: `uXjVJbKZEmw` (huidig bord); nieuw bord wordt aangemaakt tijdens implementatie.
- Bordstructuur: vrij georganiseerd — clausule-koppeling via tekstanalyse (best-effort), niet via frame-namen.
- Kleurconventie (vast): groen = positief/conform, oranje = NC, rood = NC.
