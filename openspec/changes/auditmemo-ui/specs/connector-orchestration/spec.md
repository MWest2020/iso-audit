# Spec — connector-orchestration (nieuw)

## ADDED Requirements

### Requirement: Source triggeren via de UI

De UI MUST een geregistreerde `iso_audit.sources`-adapter kunnen kiezen en de
ingest ervan triggeren tot een findings-dataset, als opstap naar draft → review
→ memo. De UI MUST de bestaande sources-registry gebruiken (geen herimplementatie
van connectoren).

#### Scenario: Drive-source triggeren

- **WHEN** de auditor in de UI de `drive`-source kiest en ingest start
- **THEN** wordt de bestaande DriveSource-adapter gebruikt om documenten op te halen
- **AND** stroomt het resultaat als findings-dataset door naar de draft/review-stap

### Requirement: Expliciete config, geen stille fallback

De connector-trigger MUST dezelfde expliciete-config-discipline volgen als de CLI:
ontbrekende credentials/config geven een heldere fout in de UI, geen stille
fallback of verzonnen data.

#### Scenario: Ontbrekende credentials

- **WHEN** een source getriggerd wordt zonder de vereiste credentials/config
- **THEN** toont de UI een duidelijke fout en wordt geen lege of verzonnen findings-set geproduceerd
