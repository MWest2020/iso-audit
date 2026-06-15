# Spec — auditmemo (nieuw)

## ADDED Requirements

### Requirement: Memo-generatie command

Het `iso-audit memo` subcommand MUST een management-memo genereren uit een
findings-dataset, een profiel en een historical-NCs-register, en zowel HTML als
PDF wegschrijven naar het opgegeven output-pad.

#### Scenario: Reguliere memo-run

- **WHEN** `iso-audit memo --profile <slug> --findings <path> --historical-ncs <path> --output <path>` wordt aangeroepen met geldige inputs
- **THEN** wordt een HTML- én een PDF-bestand geschreven naar `<path>`
- **AND** bevat de memo de cover, lead-summary, context, NC-blokken, verbeterpunt(en), historical-NC-tabel en footer

### Requirement: NC-extractie uit findings

De memo MUST voor elke finding met `severity == "NC"` een NC-blok opnemen; geen
enkele NC mag worden weggelaten.

#### Scenario: Findings met twee NC's

- **WHEN** de findings-dataset twee findings met severity `NC` bevat
- **THEN** bevat de memo precies twee NC-blokken, elk met clausule-referentie, norm-citaat, afwijkingsbeschrijving en action-table

### Requirement: Verbeterpunt-extractie

De memo MUST OFI's als verbeterpunt opnemen wanneer een configureerbare drempel
is overschreden (bv. `>= 10` OFI's op één clausule) of wanneer een finding
`promote_to_improvement: true` heeft.

#### Scenario: OFI met expliciete promotie-flag

- **WHEN** een finding severity `OFI` heeft en `promote_to_improvement: true`
- **THEN** verschijnt deze als verbeterpunt-sectie met verplichte classificatie-rationale ("waarom verbeterpunt en geen NC?")

### Requirement: Pattern-detectie in NC-context

De memo MUST cross-clause-patronen ("X positieve bevindingen op clausule Y vs Z
OFI's op dezelfde clausule") automatisch genereren en in de NC-context tonen.

#### Scenario: Gemengde clausule

- **WHEN** een clausule zowel substantiële positieve bevindingen als OFI's heeft
- **THEN** bevat het bijbehorende NC-blok een automatisch gegenereerde patroon-zin die uitvoering en vastlegging onderscheidt

### Requirement: Genormeerd citaat met hard-fail

Elk NC- en verbeterpunt-blok MUST de norm-tekst van elke geciteerde clausule uit
de norm-database tonen. Een blok MUST meerdere clausules kunnen citeren (bv. NC 2
in het referentievoorbeeld citeert §6.5, §5.11 en §5.18 als aparte norm-blokken).
Een ontbrekende clausule MUST een harde fout veroorzaken; de memo mag nooit een
verzonnen norm-citaat bevatten.

#### Scenario: NC met meerdere clausules

- **WHEN** een NC-blok naar §6.5, §5.11 en §5.18 verwijst
- **THEN** toont het blok drie afzonderlijke genormeerde citaten, elk uit de norm-database

#### Scenario: Onbekende clausule

- **WHEN** een NC verwijst naar een clausule die niet in de norm-database staat
- **THEN** faalt de memo-generatie met een duidelijke fout en wordt geen output geschreven

### Requirement: Data-gedreven context-sectie

De context-sectie MUST uit configuratie/findings worden opgebouwd met: auditcyclus,
scope per norm (geauditeerde hoofdstukken), geraadpleegde bronnen inclusief de
findings-dataset-telling (totaal + per severity), en bespreking (datum + met wie,
placeholder indien nog niet gepland).

#### Scenario: Bronnen met dataset-telling

- **WHEN** de context-sectie wordt gerenderd voor een dataset van 436 bevindingen (2 NC, 297 OFI, 122 positief, 15 niet-geclassificeerd)
- **THEN** toont "Geraadpleegde bronnen" die aantallen, en is de bespreking-regel een gemarkeerde placeholder als geen datum is opgegeven

### Requirement: Action-table per NC met gemarkeerde placeholders

Elk NC-blok MUST een action-table met de kolommen `wat`, `wie`, `waar`,
`uiterlijk` bevatten. Placeholders zijn toegestaan maar MUST visueel gemarkeerd
zijn (CSS-class `.placeholder`, italic + muted).

#### Scenario: Ontbrekende eigenaar

- **WHEN** voor een actie geen eigenaar is opgegeven
- **THEN** toont de `wie`-cel een placeholder met class `.placeholder` (bv. "eigenaar in te vullen") in plaats van een verzonnen naam

### Requirement: Configureerbare voorbehoud-secties

De context-sectie MUST per memo-run configureerbare voorbehouden ondersteunen:
auditscope en (conditioneel) auditor-onafhankelijkheid.

#### Scenario: Onafhankelijkheid-voorbehoud aan

- **WHEN** het profiel of de run `include_independence_caveat` op true zet
- **THEN** bevat de context-sectie het auditor-onafhankelijkheid-voorbehoud; anders wordt het weggelaten

### Requirement: Self-contained output

De gerenderde memo MUST self-contained zijn: het logo wordt inline als SVG
opgenomen en fonts via een CSS-stack, zonder externe assets of
download-afhankelijkheden tijdens het renderen.

#### Scenario: PDF zonder externe refs

- **WHEN** de PDF wordt gegenereerd
- **THEN** bevat de output geen verwijzingen naar externe bestanden of URL's voor logo of fonts

### Requirement: Audit-trail-metadata

De gerenderde memo MUST een onzichtbare audit-trail bevatten met profile-slug,
profile-versie, tool-versie, render-timestamp en findings-dataset-hash, in een
HTML-comment en in de PDF-metadata.

#### Scenario: Memo herleidbaar naar bron

- **WHEN** een gegenereerde memo wordt geïnspecteerd
- **THEN** zijn profile-slug, profile-versie, tool-versie, render-timestamp en findings-dataset-hash uit de HTML-comment (en PDF-metadata) af te lezen

### Requirement: Reproductie van het referentievoorbeeld

De memo-generator MUST uit een gestructureerde input een memo produceren die
structureel equivalent is aan `Auditmemo_management_2026-05-06_v2.pdf` (zelfde
secties en volgorde; niet pixel-exact).

#### Scenario: Render uit voorbeeld-input

- **WHEN** gerenderd uit `examples/findings.json` + `examples/historical_ncs.yaml` + voorbeeldprofiel
- **THEN** is de HTML lxml-valid, rendert de PDF zonder WeasyPrint-warnings, en bevat de output dezelfde secties als het referentie-PDF
