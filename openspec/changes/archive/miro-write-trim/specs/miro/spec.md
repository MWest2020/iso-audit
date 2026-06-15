# Miro capability (post-trim)

## ADDED Requirements

### Requirement: Miro-integratie is READ-only

Het systeem SHALL Miro uitsluitend als bron-systeem behandelen voor
auditor-notities. Het SHALL geen Miro-API-calls doen die boards,
frames, sticky-notes, items of metadata creëren of muteren als
onderdeel van een pipeline- of CLI-run.

De gedeelde HTTP-laag (`MiroClient`) MAG `POST`-methodes blijven
exporteren als API-symmetrie, maar deze SHALL niet vanuit
productie-code worden aangeroepen.

#### Scenario: Pipeline raakt Miro write-API niet

- **WHEN** `iso-audit pipeline --source drive` of `--source miro` wordt
  uitgevoerd, in elke `--mode` of `--notifier`-configuratie
- **THEN** geen HTTP `POST` of `PATCH`-request MUST naar
  `api.miro.com/v2/*` gaan
- **AND** netwerk-trace MUST alleen `GET`-requests bevatten

#### Scenario: CLI heeft geen subcommand voor write-flow

- **WHEN** `iso-audit --help` wordt aangeroepen
- **THEN** geen subcommand met de naam `create-board`,
  `setup-interview`, of vergelijkbaar MUST in de subcommand-lijst
  verschijnen
- **AND** geen flag op `pipeline` MUST een Miro-write triggeren

## REMOVED Requirements

### Requirement: ~~Miro audit-bord aanmaakautomatisme~~

**Reden voor verwijdering:** Miro biedt sinds Q4 2025 een ingebouwde
AI-tool die uit een prompt een audit-bord met frames + sticky's kan
genereren. De auditor heeft meer controle via die route (real-time
layout-aanpassing) en de Python-implementatie was 31% getest en
weinig onderhoudbaar (API-contract-quirks rond frame-positie + rate-
limiting).

### Requirement: ~~Miro interview-bord generator~~

**Reden voor verwijdering:** Hetzelfde argument. Het opzetten van
sticky-notes per ongedekte clausule kan de auditor zelf doen via Miro-
AI of een vraag-template-doc; het Python-pad was 47% getest en bracht
geen schaalvoordeel.

## REPLACES

De handleiding `docs/miro-auditor-bord-prompt.md` en
`docs/miro-interview-prompt.md` (toegevoegd in deze change) bieden de
auditor twee voorbeeld-prompts die in Miro-AI geplakt kunnen worden om
in één klik hetzelfde resultaat te krijgen.
