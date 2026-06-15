## ADDED Requirements

### Requirement: Clausule-mapping laden uit configuratiebestand
Het systeem SHALL de koppeling tussen norm-clausules en zoektermen laden uit een versiebeheerd `clause_map.yaml`-bestand per norm.

#### Scenario: ISO 9001 mapping geladen
- **WHEN** de audit wordt gestart voor ISO 9001
- **THEN** laadt het systeem `config/clause_map_9001.yaml` met clausules 4 t/m 10 en bijbehorende zoektermen/documenttypen

#### Scenario: ISO 27001 mapping geladen
- **WHEN** de audit wordt gestart voor ISO 27001
- **THEN** laadt het systeem `config/clause_map_27001.yaml` met alle Annex A controls en bijbehorende zoektermen

### Requirement: Documenten koppelen aan clausules
Het systeem SHALL elk ingelezen document koppelen aan één of meer norm-clausules op basis van de clause_map, en de koppeling opslaan als gestructureerde data.

#### Scenario: Document gekoppeld aan clausule
- **WHEN** een document relevante zoektermen bevat voor clausule 6.1 (risicobeoordeling)
- **THEN** wordt het document gekoppeld aan clausule 6.1 in de auditmatrix

#### Scenario: Document zonder clausule-match
- **WHEN** een document geen zoektermen matcht met enige clausule
- **THEN** wordt het document gemarkeerd als "niet-geclassificeerd" en opgenomen in het validatierapport

### Requirement: Ontbrekende clausuledekking signaleren
Het systeem SHALL na koppeling rapporteren welke verplichte clausules geen gekoppeld document hebben.

#### Scenario: Ontbrekende bewijsstukken gedetecteerd
- **WHEN** clausule 8.2 (klantgerichtheid) geen gekoppeld document heeft
- **THEN** verschijnt clausule 8.2 in de lijst "ontbrekende bewijsstukken" in het validatierapport
