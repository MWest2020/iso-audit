# Spec — norm-database (nieuw)

## ADDED Requirements

### Requirement: Plug-in norm-database

De norm-database MUST plug-in zijn: elk `<standard-slug>.yaml` in `data/norms/`
(of een door de gebruiker opgegeven pad) wordt geladen. Normen MUST niet
hardcoded zijn, zodat latere standaarden (14001/22301/42001) zonder code-wijziging
toegevoegd kunnen worden.

#### Scenario: Extra norm-bestand

- **WHEN** een nieuw `data/norms/<slug>.yaml` wordt toegevoegd
- **THEN** is die standaard beschikbaar voor profielen en memo-generatie zonder codewijziging

### Requirement: Meertalige clausule-lookup

De norm-lookup MUST per clausule een titel en tekst in de geconfigureerde taal
teruggeven; de MVP MUST NL en EN ondersteunen.

#### Scenario: NL-lookup

- **WHEN** een memo in taal `nl` clausule `6.5` opvraagt
- **THEN** levert de lookup `title_nl` en `text_nl` van die clausule

### Requirement: Hard-fail bij ontbrekende clausule

Een lookup van een clausule die niet in de norm-database staat MUST een harde
fout veroorzaken. De tool mag nooit een ontbrekend citaat stilzwijgend overslaan
of verzinnen.

#### Scenario: Niet-bestaande clausule

- **WHEN** een NC verwijst naar clausule `9.9` die niet in de norm-database bestaat
- **THEN** faalt de generatie met een fout die de ontbrekende clausule en standaard noemt

### Requirement: MVP-clausuledekking

De MVP-norm-databases voor ISO 9001:2015 en ISO 27001:2022 MUST minimaal de
clausules uit het referentievoorbeeld bevatten: 4.4, 5.11, 5.18, 5.24, 5.27,
6.3, 6.5, 8.13, 8.15, 8.16, 10.1 en 10.2.

#### Scenario: Referentie-memo resolvet alle clausules

- **WHEN** de referentie-memo wordt gegenereerd
- **THEN** resolvet elke geciteerde clausule in de meegeleverde norm-databases zonder hard-fail
