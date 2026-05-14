## 1. Infrastructuur & Configuratie

- [x] 1.1 Verifieer beschikbare GSuite MCP-tools (Drive, Docs, Sheets, Slides, Gmail, Calendar) en documenteer vereiste OAuth-scopes
- [x] 1.2 Verifieer beschikbare Miro MCP/API-koppeling en documenteer vereiste Miro-scopes (boards:read)
- [x] 1.3 Maak `config/clause_map_9001.yaml` aan met clausules 4-10 en bijbehorende zoektermen
- [x] 1.4 Maak `config/clause_map_27001.yaml` aan met Annex A controls en bijbehorende zoektermen
- [x] 1.5 Maak `.env.example` aan met placeholder-instructies (geen echte waarden) voor GSuite service account pad en Miro API token
- [x] 1.6 Verifieer dat `.env` in `.gitignore` staat en nooit gecommit wordt

## 2. Audit Report Template

- [x] 2.1 Lees bestaand auditrapport uit Drive-map "Interne Audits" en analyseer structuur als basis voor template
- [x] 2.2 Definieer gecombineerde rapportstructuur: ISO 9001 als basis + ISO 27001 Annex A als addendum
- [x] 2.3 Maak Google Docs-template aan met alle verplichte secties en `{{placeholder_naam}}`-velden
- [x] 2.4 Voeg koptekst toe met template-versie (v1.0), aanmaakdatum en toepasselijke norm(en)
- [x] 2.5 Verifieer dat alle placeholders programmatisch vervangbaar zijn

## 3. Miro Ingestion

- [x] 3.1 Implementeer Miro-ingest: sticky notes en tekstvakken ophalen uit geconfigureerde board-ID('s) via MCP/API
- [x] 3.2 Implementeer frame-naam → clausule koppeling (bijv. frame "6.1 Risicobeoordeling" → clausule 6.1)
- [x] 3.3 Implementeer optionele kleur-mapping voor pre-classificatie (rood=NC, oranje=OFI, groen=positief)
- [x] 3.4 Implementeer samenvoegen van Miro-notities met Drive-bevindingen tot één invoerlijst met herkomst-label
- [x] 3.5 Valideer: geen Miro-borden gevonden geeft waarschuwing maar stopt de pipeline niet

## 4. Document Ingestion

- [x] 4.1 Implementeer Drive-ingest: documenten ophalen uit de "Interne Audits"-map en submappen via MCP
- [x] 4.2 Implementeer detectie van niet-tekstuele bestanden (scans/afbeeldingen) → toevoegen aan `handmatige_review`-lijst
- [x] 4.3 Implementeer batchverwerking (max 20 documenten per batch) met exponential backoff bij rate-limit (max 3 retries, max 30s wachttijd)
- [x] 4.4 Valideer: lege map geeft duidelijke foutmelding en stopt pipeline

## 5. Clausule-Mapping

- [x] 5.1 Implementeer laden van `clause_map_<norm>.yaml` op basis van gekozen norm
- [x] 5.2 Implementeer koppeling van documenten aan clausules via zoekterm-matching
- [x] 5.3 Implementeer detectie en rapportage van documenten zonder clausule-match ("niet-geclassificeerd")
- [x] 5.4 Implementeer rapportage van ontbrekende clausuledekking (clausules zonder enig document)

## 6. Bevindingen Classificatie

- [x] 6.1 Implementeer Claude-gebaseerde classificatie van bevindingen (NC / OFI / positief) per clausule-invoer-paar (Drive én Miro)
- [x] 6.2 Zorg dat alle beschrijvingen in het Nederlands worden gegenereerd
- [x] 6.3 Implementeer menselijke reviewstap: toon overzicht (incl. herkomst Drive/Miro) en vraag bevestiging/correctie vóór verdere verwerking
- [x] 6.4 Implementeer opslaan van alle bevindingen naar Google Sheets (kolommen: clausule, herkomst, classificatie, beschrijving, status)

## 7. Rapportgeneratie

- [x] 7.1 Implementeer kopiëren van template naar nieuw Google Docs-bestand met gestandaardiseerde bestandsnaam (`Auditrapport_<norm>_<JJJJ-MM-DD>`)
- [x] 7.2 Implementeer vullen van alle `{{placeholder_naam}}`-velden met auditdata
- [x] 7.3 Implementeer waarschuwing bij resterende lege placeholders na invullen
- [x] 7.4 Implementeer generatie van Nederlandse management summary (max 300 woorden, top-3 aandachtspunten)
- [x] 7.5 Implementeer groepering van bevindingen per clausule gesorteerd op ernst (NC → OFI → positief)
- [x] 7.6 Implementeer ISO 27001 Annex A addendum-sectie als aparte rapportdivisie
- [x] 7.7 Sla rapport op in Drive-map "Interne Audits"

## 8. Slide Summary

- [x] 8.1 Implementeer aanmaken van Google Slides-presentatie met de 5 verplichte slides
- [x] 8.2 Implementeer selectie van top-3 bevindingen (NC-prioriteit, aangevuld met OFI's)
- [x] 8.3 Sla presentatie op in dezelfde Drive-map als rapport (`AuditSummary_<norm>_<JJJJ-MM-DD>`)

## 9. Notificatie & Planning

- [x] 9.1 Implementeer expliciete bevestigingsvraag vóór elke verzendactie (Calendar én Gmail)
- [x] 9.2 Implementeer Google Calendar-uitnodiging aanmaken met Drive-link naar rapport in omschrijving
- [x] 9.3 Implementeer Gmail-notificatie (optioneel) met Nederlandstalige tekst en Drive-links, geen bijlagen
- [x] 9.4 Implementeer overslaan van stap bij lege deelnemers/ontvangerslijst met log-melding

## 10. Integratie & Validatie

- [ ] 10.1 Voer end-to-end test uit met testdocumenten uit Drive "Interne Audits" én een test-Miro-bord
- [x] 10.2 Valideer dat geen secrets (GSuite + Miro tokens) in code, logs of output terechtkomen
- [x] 10.3 Documenteer vereiste Drive-mappenstructuur, Miro board-configuratie en alle configuratieparameters in README
- [x] 10.4 Controleer dat alle gegenereerde bestanden de juiste bestandsnaamconventie volgen
