## ADDED Requirements

### Requirement: i18n configuratie met EN en NL
`docusaurus.config.js` SHALL de i18n-configuratie bevatten met `defaultLocale: 'en'` en `locales: ['en', 'nl']`.

#### Scenario: Standaard locale is EN
- **WHEN** een gebruiker de site bezoekt zonder locale-prefix
- **THEN** wordt de Engelse versie getoond

#### Scenario: NL locale beschikbaar via /nl/ prefix
- **WHEN** een gebruiker navigeert naar `/nl/<pad>`
- **THEN** wordt de Nederlandse vertaling getoond als die beschikbaar is

#### Scenario: Fallback bij ontbrekende NL-vertaling
- **WHEN** een NL-vertaling voor een pagina ontbreekt
- **THEN** valt de site terug op de EN-versie zonder foutmelding

---

### Requirement: Taal-selector in navbar
De navbar SHALL een `localeDropdown`-item bevatten zodat gebruikers kunnen schakelen tussen EN en NL.

#### Scenario: Taal-selector zichtbaar
- **WHEN** de site geladen is in een browser
- **THEN** is een taal-selector zichtbaar in de navigatiebalk

#### Scenario: Schakelen naar NL
- **WHEN** een gebruiker NL selecteert in de taal-selector
- **THEN** navigeert de browser naar de NL-versie van de huidige pagina

---

### Requirement: NL-vertalingen voor alle WayOfWork-pagina's
Alle pagina's onder `website/docs/WayOfWork/` en `website/docs/ISO/` SHALL een corresponderende NL-vertaling hebben onder `website/i18n/nl/docusaurus-plugin-content-docs/current/`.

#### Scenario: NL-vertaling aanwezig voor WayOfWork-pagina
- **WHEN** een gebruiker een WayOfWork-pagina opent in de NL-locale
- **THEN** wordt de Nederlandse tekst getoond (niet de Engelse fallback)

#### Scenario: NL-vertaling markering bij draft-status
- **WHEN** een NL-vertaling nog niet door een native speaker is gereviewd
- **THEN** bevat de pagina een `:::info Vertaling in review` admonition bovenaan

---

### Requirement: Docusaurus build slaagt met i18n configuratie
De `npm run build`-opdracht in `website/` SHALL zonder fouten voltooien met de i18n-configuratie actief.

#### Scenario: Build zonder broken links
- **WHEN** `npm run build` wordt uitgevoerd
- **THEN** zijn er geen broken internal links (Docusaurus gooit een error bij `onBrokenLinks: 'throw'`)

#### Scenario: Build met alle locales
- **WHEN** `npm run build` wordt uitgevoerd
- **THEN** worden zowel de EN als de NL-versie van alle pagina's gegenereerd
