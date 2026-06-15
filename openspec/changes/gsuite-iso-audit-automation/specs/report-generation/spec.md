## ADDED Requirements

### Requirement: Template kopiëren en vullen
Het systeem SHALL het audit-report-template kopiëren naar een nieuw Google Docs-bestand en alle `{{placeholder_naam}}`-velden vullen met de auditdata.

#### Scenario: Rapport succesvol gegenereerd
- **WHEN** alle bevindingen zijn bevestigd en de rapportage-stap wordt uitgevoerd
- **THEN** bestaat er een nieuw Google Docs-bestand in de auditmap met alle secties ingevuld en geen lege placeholders

#### Scenario: Niet-ingevulde placeholder gedetecteerd
- **WHEN** na invullen nog een `{{placeholder_naam}}` aanwezig is
- **THEN** logt het systeem een waarschuwing met de naam van de ontbrekende placeholder

### Requirement: Management summary genereren
Het systeem SHALL een Nederlandse management summary schrijven (max 300 woorden) die de audituitkomst samenvat voor niet-technisch publiek.

#### Scenario: Management summary aanwezig in rapport
- **WHEN** het rapport wordt gegenereerd
- **THEN** bevat de sectie "Management Summary" een alinea met: aantal NC's, aantal OFI's, overall oordeel en top-3 aandachtspunten

### Requirement: Bevindingen gegroepeerd per clausule
Het systeem SHALL bevindingen in het rapport groeperen per norm-clausule, gesorteerd op ernst (NC eerst, dan OFI, dan positief).

#### Scenario: Volgorde bevindingen in rapport
- **WHEN** het rapport de bevindingensectie weergeeft
- **THEN** staan NC's bovenaan per clausule, gevolgd door OFI's, gevolgd door positieve observaties

### Requirement: Rapport opgeslagen in configureerbare Drive-map
Het systeem SHALL het gegenereerde rapport opslaan in een configureerbare Google Drive-map met een gestandaardiseerde bestandsnaam.

#### Scenario: Bestandsnaam conform standaard
- **WHEN** het rapport wordt opgeslagen
- **THEN** is de bestandsnaam: `Auditrapport_<norm>_<JJJJ-MM-DD>.docx` (bijv. `Auditrapport_ISO9001_2026-03-13`)
