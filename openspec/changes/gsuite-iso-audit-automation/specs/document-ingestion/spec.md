## ADDED Requirements

### Requirement: Documenten ophalen uit Google Drive
Het systeem SHALL documenten (procedures, werkinstructies, beleid) ophalen uit een configureerbare Google Drive-map via de Drive MCP-tool.

#### Scenario: Documenten succesvol ingelezen
- **WHEN** de ingest-stap wordt uitgevoerd met een geldig Drive-map-ID
- **THEN** retourneert het systeem een lijst van documenten met naam, type en tekstinhoud

#### Scenario: Lege map
- **WHEN** de opgegeven Drive-map geen ondersteunde documenten bevat
- **THEN** logt het systeem een waarschuwing en stopt de pipeline met een duidelijke foutmelding

### Requirement: Niet-tekstuele bestanden flaggen
Het systeem SHALL bestanden die geen leesbare tekst bevatten (scans, afbeeldingen, binaire bestanden) detecteren en markeren als "vereist handmatige review".

#### Scenario: Scan-PDF gedetecteerd
- **WHEN** een PDF zonder extracteerbare tekst wordt aangetroffen
- **THEN** wordt het bestand toegevoegd aan een `handmatige_review`-lijst en niet meegenomen in de automatische clausule-koppeling

### Requirement: Batchverwerking met retry-backoff
Het systeem SHALL documenten verwerken in batches van maximaal 20, met exponential backoff bij GSuite API rate-limit fouten.

#### Scenario: Rate limit bereikt
- **WHEN** de Drive API een 429-fout retourneert
- **THEN** wacht het systeem exponentieel (1s, 2s, 4s, max 30s) en herprobeert de aanvraag tot maximaal 3 keer

#### Scenario: Batch van meer dan 20 documenten
- **WHEN** de Drive-map meer dan 20 documenten bevat
- **THEN** verwerkt het systeem documenten in opeenvolgende batches van 20 tot alle documenten zijn ingelezen
