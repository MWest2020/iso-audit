## ADDED Requirements

### Requirement: Notities ophalen uit Miro-borden
Het systeem SHALL sticky notes, tekstvakken en kaarten ophalen uit geconfigureerde Miro-borden via de Miro MCP/API.

#### Scenario: Notities succesvol ingelezen
- **WHEN** de Miro-ingest-stap wordt uitgevoerd met een geldig board-ID of naampatroon
- **THEN** retourneert het systeem een gestructureerde lijst van notities met inhoud, frame-naam en (indien beschikbaar) kleur/label

#### Scenario: Geen borden gevonden
- **WHEN** geen Miro-bord overeenkomt met de geconfigureerde board-ID of naampatroon
- **THEN** logt het systeem een waarschuwing en continueert de pipeline zonder Miro-input

### Requirement: Miro-notities koppelen aan norm-clausules via tekstanalyse (best-effort)
Het systeem SHALL Miro-notities koppelen aan norm-clausules via tekstinhoud-matching tegen de clause_map. De bordstructuur is vrij georganiseerd; een exacte koppeling is niet gegarandeerd.

#### Scenario: Notitie gekoppeld via tekstinhoud
- **WHEN** een notitie zoektermen bevat die matchen met een clausule in clause_map
- **THEN** wordt de notitie gekoppeld aan die clausule

#### Scenario: Notitie zonder clausule-match
- **WHEN** een notitie geen tekstmatch heeft met enige clausule
- **THEN** wordt de notitie gemarkeerd als "niet-geclassificeerd" en gepresenteerd tijdens de menselijke reviewstap voor handmatige toewijzing

### Requirement: Sticky-kleur als classificatie (vaste conventie)
Het systeem SHALL de kleur van sticky notes interpreteren als classificatie conform de organisatieconventie: groen = positief/conform, oranje = NC-kandidaat, rood = NC.

#### Scenario: Groene sticky note ingelezen
- **WHEN** een groene sticky note wordt ingelezen
- **THEN** krijgt de bevinding pre-classificatie "positief" (ter bevestiging in de reviewstap)

#### Scenario: Oranje sticky note ingelezen
- **WHEN** een oranje sticky note wordt ingelezen
- **THEN** krijgt de bevinding pre-classificatie "NC" (ter bevestiging in de reviewstap)

#### Scenario: Rode sticky note ingelezen
- **WHEN** een rode sticky note wordt ingelezen
- **THEN** krijgt de bevinding pre-classificatie "NC" (ter bevestiging in de reviewstap)

#### Scenario: Kleur niet in conventie
- **WHEN** een sticky note een kleur heeft die niet in de conventie voorkomt
- **THEN** wordt de bevinding aangeboden zonder pre-classificatie

### Requirement: Miro-notities samenvoegen met Drive-bevindingen
Het systeem SHALL Miro-notities en Drive-documentbevindingen samenvoegen tot één geconsolideerde lijst vóór de classificatiefase.

#### Scenario: Gecombineerde invoer voor classificatie
- **WHEN** zowel Drive-documenten als Miro-notities zijn ingelezen
- **THEN** bevat de invoer voor finding-classification beide bronnen, elk gelabeld met hun herkomst (Drive / Miro)
