## ADDED Requirements

### Requirement: HWW-kern bestaat uit maximaal 6 pagina's
De `WayOfWork/`-sectie SHALL bestaan uit maximaal 6 pagina's die samen leesbaar zijn in ~30 minuten. Elke pagina heeft een duidelijke `sidebar_position` en frontmatter.

#### Scenario: Pagina-indeling correct
- **WHEN** de sidebar van de Docusaurus-site wordt geladen
- **THEN** bevat WayOfWork de volgende pagina's in volgorde: intro, organisation, way-of-work (issue flow + werkwijze), release-process, vacancies
- **AND** bevat de sectie geen stub- of duplicaatpagina's

---

### Requirement: intro.md bevat Wie we zijn (waarden + BHAG)
`WayOfWork/intro.md` SHALL de kernidentiteit van Conduction samenvatten: missie, BHAG (Big Hairy Audacious Goal: alle Nederlanders ontvangen automatisch hun rechten tegen 2035), kernwaarden (democratisch, inclusief, transparant, verantwoord, innovatief) en een verwijzing naar de volledige Intro.md voor meer context.

#### Scenario: Waarden aanwezig
- **WHEN** een medewerker intro.md leest
- **THEN** staan alle vijf kernwaarden expliciet benoemd

#### Scenario: Verwijzing naar volledige intro
- **WHEN** een medewerker meer wil weten over de markt of producten
- **THEN** is er een link naar `/docs/intro` voor het volledige overzicht

---

### Requirement: organisation.md verwijst naar organogram als leidend document
`WayOfWork/organisation.md` SHALL bovenaan een admonition bevatten die aangeeft dat het organogram leidend is en dat de pagina-inhoud ter managementbeoordeling ligt.

#### Scenario: Admonition zichtbaar
- **WHEN** organisation.md wordt geopend
- **THEN** is er een `:::caution` admonition bovenaan die de reviewstatus communiceert

#### Scenario: Organogram gerefereerd
- **WHEN** organisation.md wordt gelezen
- **THEN** is er een verwijzing naar het organogram (als extern link of ingebedde afbeelding)

---

### Requirement: Meer lezen-sectie met externe verwijzingen
Elke pagina in WayOfWork die verwijst naar externe bronnen (GitHub repos, publieke docs) SHALL een **Meer lezen**-blok bevatten aan het einde van de pagina met concrete links.

#### Scenario: GitHub-links aanwezig
- **WHEN** een medewerker een WayOfWork-pagina over werkwijze of releases leest
- **THEN** is er een sectie met links naar relevante GitHub-repos of -documenten

#### Scenario: Geen dode links
- **WHEN** Docusaurus gebuild wordt
- **THEN** zijn alle externe links syntactisch correct (Docusaurus controleert dit niet automatisch, maar links moeten handmatig geverifieerd zijn voor merge)

---

### Requirement: Vacancies.md bevat actuele vacatures en sollicitatieprocedure
`WayOfWork/Vacancies.md` SHALL actuele vacatures bevatten of expliciet aangeven dat er momenteel geen openstaande posities zijn, inclusief de GitHub-issue-gebaseerde sollicitatieprocedure.

#### Scenario: Vacature aanwezig
- **WHEN** er een openstaande vacature is
- **THEN** staat die benoemd met functietitel, locatie, uren en een link naar het GitHub-issue

#### Scenario: Geen vacatures
- **WHEN** er geen openstaande vacatures zijn
- **THEN** communiceert de pagina dit expliciet en verwijst naar het spontaan solliciteren via GitHub
