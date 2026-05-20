## ADDED Requirements

### Requirement: Claude Code kennissessie YAML is volledig en geldig
De YAML-definitie voor de Claude Code kennissessie SHALL alle verplichte velden bevatten en bruikbaar zijn als input voor de board builder.

#### Scenario: YAML bevat vier blokken
- **WHEN** de YAML geladen wordt
- **THEN** bevat deze exact 4 blokken: do's & don'ts, hoe beginnen, 7 levels roadmap, plenair

#### Scenario: Elk blok heeft een tijdsindicatie
- **WHEN** de YAML geladen wordt
- **THEN** heeft elk blok een `duur_min` veld dat optelt tot ≤ 30 minuten

### Requirement: Blok 1 — Do's & Don'ts
Het blok SHALL items bevatten voor zowel do's (kleur groen) als don'ts (kleur rood), gericht op developers zonder Claude Code ervaring.

#### Scenario: Do-items zijn groen
- **WHEN** het bord aangemaakt wordt
- **THEN** hebben alle do-items in blok 1 een groene sticky

#### Scenario: Don't-items zijn rood
- **WHEN** het bord aangemaakt wordt
- **THEN** hebben alle don't-items in blok 1 een rode sticky

### Requirement: Blok 2 — Hoe beginnen
Het blok SHALL een stap-voor-stap lijst bevatten (genummerd, kleur blauw) en minimaal één concreet voorbeeld als gele sticky.

#### Scenario: Stappenlijst aanwezig
- **WHEN** het bord aangemaakt wordt
- **THEN** bevat blok 2 minimaal 3 blauwe stickies met genummerde stappen

#### Scenario: Concreet voorbeeld aanwezig
- **WHEN** het bord aangemaakt wordt
- **THEN** bevat blok 2 minimaal 1 gele sticky met een voorbeeld

### Requirement: Blok 3 — 7 Levels roadmap
Het blok SHALL alle 7 levels uit het Simon Scrapes-framework weergeven als stickies, visueel als oplopend pad (niveau-nummering zichtbaar).

#### Scenario: Alle 7 levels aanwezig
- **WHEN** het bord aangemaakt wordt
- **THEN** bevat blok 3 exact 7 stickies, elk met levelnummer en naam

#### Scenario: Beginnersniveaus gemarkeerd
- **WHEN** het bord aangemaakt wordt
- **THEN** zijn levels 1-3 visueel onderscheiden als "in scope voor beginners" (afwijkende kleur of label)

### Requirement: Blok 4 — Plenair
Het blok SHALL minimaal 2 open discussievragen bevatten als gele stickies, plus lege stickies als ruimte voor deelnemersinput.

#### Scenario: Discussievragen aanwezig
- **WHEN** het bord aangemaakt wordt
- **THEN** bevat blok 4 minimaal 2 gele stickies met open vragen

#### Scenario: Ruimte voor input
- **WHEN** het bord aangemaakt wordt
- **THEN** bevat blok 4 minimaal 3 lege lichtgrijze stickies voor deelnemersinput
