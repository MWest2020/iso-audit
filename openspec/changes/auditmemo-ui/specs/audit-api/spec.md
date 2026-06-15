# Spec — audit-api (nieuw)

## ADDED Requirements

### Requirement: Lokale API over de bestaande motor

De tool MUST een lokale HTTP-API bieden (gebonden aan 127.0.0.1) die de
auditor-flow-stappen blootlegt — landscape, run, triage, memo — door de
bestaande motor aan te roepen (`reporting/landscape`, `run_audit`, `memo.draft`,
`builder`/`renderer`, `sources`-registry), zonder die logica te herimplementeren.

#### Scenario: Memo via de API

- **WHEN** een client `POST /memo` aanroept met een findings-/triage-set
- **THEN** levert de API hetzelfde resultaat als `iso-audit memo` voor dezelfde input (HTML + PDF)

### Requirement: Append-only triage en reclassificatie

Reclassificatie (NC↔OFI) en triage-statuswijzigingen via de API MUST append-only
in de bestaande `decisions`/`classifications`-tabellen worden vastgelegd — nooit
overschrijven — met actor, timestamp en reden, zodat elke memo herleidbaar blijft.

#### Scenario: NC naar OFI ompennen

- **WHEN** de auditor een finding van NC naar OFI reclassificeert via de API
- **THEN** wordt een nieuwe (append-only) record vastgelegd met de override, actor, timestamp en reden
- **AND** blijft de oorspronkelijke classificatie in de trail bewaard

#### Scenario: Triage-status zetten

- **WHEN** de auditor een kandidaat-NC op "nader_onderzoek" zet
- **THEN** wordt die keuze append-only vastgelegd en weerspiegeld in de volgende memo-render

### Requirement: Verwisselbare frontend zonder eigen logica

De frontend MUST een dunne client van de API zijn: alle beslissingen en
assemblage lopen via de API (en daarmee de motor), zodat de frontend
vervangbaar is (minimale web nu, Nextcloud later) zonder gedragsverandering.

#### Scenario: Frontend vervangen

- **WHEN** een andere frontend dezelfde API-endpoints aanroept
- **THEN** is het resultaat (triage-trail, memo) identiek, omdat de logica in de API/motor zit
