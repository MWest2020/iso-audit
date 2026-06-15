## Context

De Docusaurus-site (v2.4.3) op docs.conduction.nl is geconfigureerd met alleen `en` als locale. De `website/docs/WayOfWork/`-sectie is de basis voor het nieuwe handboek, maar bevat verouderde en incomplete content. Naast de WayOfWork-sectie bevat de site stub-bestanden en een uitgebreide Products-sectie die niet thuishoort in een medewerkershandboek.

ISO 9001:2015 en ISO 27001:2022 zijn beide actief. De norm vereist dat kwaliteitsbeleid, informatiebeveiligingsbeleid, rollen/verantwoordelijkheden, incidentmelding en competentievereisten gedocumenteerd en aantoonbaar communiceerbaar zijn aan medewerkers. Dit handboek is het primaire communicatiekanaal daarvoor.

Alle wijzigingen vinden plaats in de geclonede repo `/home/gongoeloe/projects/.github/` op branch `feature/hww-2.0`.

## Goals / Non-Goals

**Goals:**
- Docusaurus i18n activeren met EN (default) + NL, inclusief taal-selector in navbar
- WayOfWork-sectie herstructureren als compacte HWW-kern (~5-6 pagina's) in beide talen
- ISO-verplichte pagina's (kwaliteitsbeleid, IB-beleid, incidentmelding) toevoegen als aparte docs
- Stubs, duplicaten en niet-relevante pagina's verwijderen
- organisation.md outdated-secties flaggen en klaarzetten voor managementbeoordeling

**Non-Goals:**
- Inhoudelijke wijzigingen aan root-niveau community-bestanden (CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md)
- Aanpassingen aan GitHub Actions workflows
- Automatisch inlezen van ISO-drive documenten (read-only check valt buiten scope van deze Docusaurus-wijziging)
- Volledige herziening van Products/-sectie inhoud (alleen reduceren tot verwijzing)

## Decisions

### D1: Docusaurus native i18n vs. externe vertaaltool
**Beslissing**: Docusaurus native i18n gebruiken (`i18n` config in `docusaurus.config.js`, NL-bestanden in `website/i18n/nl/docusaurus-plugin-content-docs/`).

**Waarom**: Geen extra tooling nodig, werkt out-of-the-box met Docusaurus v2, NL-bestanden zijn gewone Markdown in dezelfde mappenstructuur als EN. Alternatief (Crowdin/Transifex) voegt onnodige complexiteit toe voor een team van deze grootte.

### D2: EN als defaultLocale, NL als tweede locale
**Beslissing**: `defaultLocale: 'en'`, `locales: ['en', 'nl']`.

**Waarom**: De bestaande content is EN en de codebase/GitHub-integratie werkt op EN. NL is de primaire taal voor interne medewerkers, maar EN blijft leidend voor externe leesbaarheid en GitHub-context. Omgekeerde volgorde zou alle bestaande links en CI breken.

### D3: ISO-beleidspagina's als aparte Docusaurus-docs, niet inline in WayOfWork
**Beslissing**: Nieuwe map `website/docs/ISO/` met afzonderlijke pagina's per beleid.

**Waarom**: ISO-documenten hebben een eigen reviewcyclus (managementbeoordeling) en moeten versioneerbaar en verwijsbaar zijn los van de werkwijzedocumentatie. Inline in WayOfWork vermengt governance met operationele content.

### D4: Products/-sectie reduceren tot enkelvoudige verwijzingspagina
**Beslissing**: Alle losse Products/-bestanden samenvoegen tot één `Products/overview.md` met links, en de rest verwijderen.

**Waarom**: De Products-content is marketingmateriaal en hoort niet in een medewerkershandboek. Volledig verwijderen zou broken links in de sidebar opleveren; een enkele verwijzingspagina is de minst verrassende oplossing.

## Risks / Trade-offs

- **[Risk] NL-vertalingen zijn handmatig werk** → Mitigatie: Start met machine-vertaling als basis, markeer als "in review" totdat een native speaker heeft goedgekeurd. Geen blocker voor de branch.
- **[Risk] organisation.md heeft verwijzingen naar outdated structuur** → Mitigatie: Voeg een prominente `:::caution` Docusaurus-admonition toe bovenaan de pagina en maak een GitHub Issue voor managementbeoordeling. Niet blokkend voor de merge.
- **[Risk] ISO-beleidspagina's zijn placeholder totdat management ze heeft goedgekeurd** → Mitigatie: Markeer met `draft: true` in de frontmatter en voeg een admonition toe. De pagina's zijn aanwezig maar communiceren duidelijk dat ze ter beoordeling liggen.
- **[Risk] Docusaurus `onBrokenLinks: 'throw'` zorgt voor build failures bij verwijderde pagina's** → Mitigatie: Verwijder sidebar-entries gelijktijdig met pagina's; run `npm run build` lokaal ter verificatie.

## Migration Plan

1. i18n config aanpassen in `docusaurus.config.js`
2. Sidebar updaten (`sidebars.js`) om nieuwe structuur te reflecteren
3. Content cleanup uitvoeren (verwijderingen)
4. WayOfWork-pagina's herschrijven/herstructureren (EN)
5. ISO-beleidspagina's aanmaken (EN, als draft)
6. NL-vertalingen aanmaken onder `i18n/nl/`
7. Lokale build valideren (`npm run build` in `website/`)
8. PR openen naar `main` voor review

Rollback: branch `feature/hww-2.0` is geïsoleerd; main blijft ongewijzigd.

## Open Questions

- **OQ1**: Zijn het kwaliteitsbeleid en informatiebeveiligingsbeleid momenteel in de ISO-drive als afzonderlijk document, of alleen in het oude handboek? (Bepaalt of we de tekst kunnen overnemen of opnieuw moeten opstellen.)
- **OQ2**: Is er een actueel organogram beschikbaar als exporteerbaar bestand (SVG/PNG) voor in organisation.md?
- **OQ3**: Wie is de NL-reviewende persoon voor de vertalingen?
