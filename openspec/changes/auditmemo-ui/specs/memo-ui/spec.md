# Spec — memo-ui (nieuw)

## ADDED Requirements

### Requirement: Lokale auditor-UI

De tool MUST een lokale web-UI starten (standaard gebonden aan 127.0.0.1,
single-user, geen externe expositie) die bovenop de bestaande draft-/render-motor
draait — zonder de memo-logica opnieuw te implementeren.

#### Scenario: UI starten

- **WHEN** de auditor `iso-audit ui` draait
- **THEN** start een lokale server op 127.0.0.1 en toont een review-pagina
- **AND** worden geen poorten op externe interfaces geopend

### Requirement: Review en redactie van kop-NC's

De UI MUST de gedrafte kop-NC's tonen en per blok titel, afwijking, corrigerende
maatregel en action-table laten redigeren; de edits MUST terug naar de
findings/memo-input geschreven worden zodat `build_memo` de enige assemblage-route
blijft.

#### Scenario: Maatregel redigeren

- **WHEN** de auditor de corrigerende maatregel van een kop-NC aanpast en opslaat
- **THEN** wordt de wijziging in de onderliggende findings/memo-input opgeslagen
- **AND** reflecteert een nieuwe render de aangepaste tekst

### Requirement: Live preview en PDF-export

De UI MUST een HTML-preview van de memo tonen en een PDF-export bieden via de
bestaande renderer (WeasyPrint), met dezelfde self-contained output en
audit-trail-metadata als de CLI.

#### Scenario: PDF exporteren

- **WHEN** de auditor op "exporteer PDF" klikt
- **THEN** levert de UI hetzelfde PDF als `iso-audit memo` voor dezelfde input
- **AND** bevat de output de audit-trail-metadata (findings-hash, timestamp)
