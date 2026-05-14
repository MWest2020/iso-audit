## ADDED Requirements

### Requirement: Google Slides presentatie genereren
Het systeem SHALL een Google Slides-presentatie aanmaken met een executive summary van de audituitkomst, bedoeld voor managementpresentatie.

#### Scenario: Presentatie succesvol aangemaakt
- **WHEN** de slide-stap wordt uitgevoerd na rapportgeneratie
- **THEN** bestaat er een Google Slides-bestand in de auditmap met minimaal de verplichte slides

### Requirement: Verplichte slides
De presentatie SHALL minimaal de volgende slides bevatten: titelpagina, auditscope & doel, samenvatting resultaten (NC/OFI/positief tellers), top-3 bevindingen, aanbevolen actiepunten.

#### Scenario: Alle verplichte slides aanwezig
- **WHEN** de presentatie wordt geopend
- **THEN** bevat deze exact: slide 1 (titel + datum + norm), slide 2 (scope), slide 3 (resultaatoverzicht), slide 4 (top-3 bevindingen), slide 5 (actiepunten)

#### Scenario: Top-3 bevindingen geselecteerd op ernst
- **WHEN** er meer dan 3 NC's zijn
- **THEN** toont slide 4 de 3 NC's met hoogste ernst; bij minder dan 3 NC's worden OFI's aangevuld tot top-3

### Requirement: Presentatie opgeslagen in zelfde auditmap als rapport
Het systeem SHALL de presentatie opslaan in dezelfde Drive-map als het auditrapport.

#### Scenario: Bestandsnaam conform standaard
- **WHEN** de presentatie wordt opgeslagen
- **THEN** is de bestandsnaam: `AuditSummary_<norm>_<JJJJ-MM-DD>` (bijv. `AuditSummary_ISO9001_2026-03-13`)
