## ADDED Requirements

### Requirement: Template aanmaken in Google Docs
Het systeem SHALL een herbruikbaar auditrapport-template aanmaken als Google Docs-document in een configureerbare Drive-map, conform de structuureisen van ISO 9001:2015 en ISO 27001:2022.

#### Scenario: Template succesvol aangemaakt
- **WHEN** de gebruiker de template-aanmaakstap uitvoert voor een gekozen norm (9001 of 27001)
- **THEN** verschijnt er een nieuw Google Docs-bestand in de opgegeven Drive-map met alle verplichte secties en named placeholders

#### Scenario: Template bevat verplichte secties
- **WHEN** het template wordt geopend
- **THEN** bevat het minimaal de secties: Auditdoel, Scope, Auditteam, Uitvoeringsperiode, Referentienorm, Management Summary, Bevindingen (NC/OFI/positief), Conclusie, Handtekeningblok

### Requirement: Named placeholders in template
Het template SHALL named placeholders bevatten die programmatisch gevuld kunnen worden, in de vorm `{{placeholder_naam}}`.

#### Scenario: Placeholders herkenbaar voor vulstap
- **WHEN** de report-generation capability het template kopieert
- **THEN** kan elk `{{placeholder_naam}}`-veld worden vervangen door de corresponderende auditdata zonder handmatige bewerking

### Requirement: Template versie en normdatum vastleggen
Het template SHALL in de koptekst de template-versie en de normdatum (bijv. "ISO 9001:2015") bevatten.

#### Scenario: Versie-informatie aanwezig bij aanmaak
- **WHEN** het template wordt aangemaakt
- **THEN** staat in de koptekst: template-versie (bijv. v1.0), aanmaakdatum en toepasselijke norm
