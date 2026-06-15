## ADDED Requirements

### Requirement: Stub-bestanden verwijderd uit de docs-structuur
De volgende bestanden SHALL verwijderd zijn omdat ze alleen een lege heading bevatten en geen content toevoegen: `Market.md`, `Partners.md`, `WayOfWork/competences.md`, `knowledge/intro.md`.

#### Scenario: Verwijderde bestanden niet meer in sidebar
- **WHEN** de Docusaurus-sidebar geladen wordt
- **THEN** zijn Market, Partners, Competences en Knowledge intro niet meer aanwezig als navigatie-items

#### Scenario: Geen broken links door verwijderingen
- **WHEN** `npm run build` uitgevoerd wordt
- **THEN** zijn er geen interne links die verwijzen naar de verwijderde bestanden

---

### Requirement: join.md verwijderd als duplicaat
`WayOfWork/join.md` SHALL verwijderd zijn omdat de inhoud identiek is aan `Issue_flow.md`.

#### Scenario: join.md niet aanwezig
- **WHEN** het bestandssysteem van de docs-map geïnspecteerd wordt
- **THEN** bestaat `website/docs/WayOfWork/join.md` niet meer

---

### Requirement: Nextcon.md verwijderd als intern projectdocument
`Products/Projects/Nextcon.md` SHALL verwijderd zijn omdat het een intern migratieproject betreft dat niet thuishoort in publieke documentatie.

#### Scenario: Nextcon niet zichtbaar in docs
- **WHEN** de Docusaurus-site gebuild en geopend wordt
- **THEN** is er geen pagina of sidebar-item voor NEXTCon

---

### Requirement: Products/-sectie gereduceerd tot één verwijzingspagina
Alle losse Products/-bestanden (Consultancy.md, Market.md, Partners.md, Pricing.md, Services.md, Training.md, Components.md, en de lege projectpagina's) SHALL vervangen worden door één `Products/overview.md` met een korte beschrijving en links naar externe bronnen.

#### Scenario: Eén Products-pagina aanwezig
- **WHEN** de sidebar geladen wordt
- **THEN** is er één item onder Products (of Products is verplaatst naar een externe link in de footer)

#### Scenario: Originele dienstpagina's niet meer als losse docs beschikbaar
- **WHEN** `website/docs/Products/` geïnspecteerd wordt
- **THEN** bestaan alleen `overview.md` (of equivalent) en geen losse Consultancy/Pricing/Services/etc. bestanden meer

---

### Requirement: knowledge/-sectie verwijderd
De `knowledge/`-map inclusief `intro.md` SHALL verwijderd zijn omdat er geen content aanwezig is en de sectie geen toegevoegde waarde heeft in de huidige scope.

#### Scenario: knowledge-sectie afwezig
- **WHEN** `website/docs/knowledge/` geïnspecteerd wordt
- **THEN** bestaat de map niet meer (of is leeg en uit de sidebar verwijderd)
