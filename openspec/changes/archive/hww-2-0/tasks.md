## 1. i18n Configuratie

- [x] 1.1 Voeg `nl` toe aan `locales` in `website/docusaurus.config.js` (`i18n: { defaultLocale: 'en', locales: ['en', 'nl'] }`)
- [x] 1.2 Voeg `localeDropdown` toe aan navbar items in `docusaurus.config.js`
- [x] 1.3 Maak de i18n-mappenstructuur aan: `website/i18n/nl/docusaurus-plugin-content-docs/current/`

## 2. Content Cleanup

- [x] 2.1 Verwijder `website/docs/Products/Market.md`, `Products/Partners.md`, `Products/Projects/InnovatieProjecten.md`, `Products/Projects/Nextcon.md`
- [x] 2.2 Verwijder `website/docs/Products/Consultancy.md`, `Products/Pricing.md`, `Products/Services.md`, `Products/Training.md`, `Products/Components.md`
- [x] 2.3 Maak `website/docs/Products/overview.md` aan als enkelvoudige verwijzingspagina (links naar conduction.nl, GitHub)
- [x] 2.4 Verwijder `website/docs/WayOfWork/competences.md` en `WayOfWork/join.md`
- [x] 2.5 Verwijder `website/docs/knowledge/intro.md` en de `knowledge/`-map
- [x] 2.6 Verwijder `website/docs/Products/Intro.md` (vervangen door overview.md)
- [x] 2.7 Verwijder `website/docs/Diagrams/` map indien geen actieve links ernaar bestaan

## 3. Sidebar Updaten

- [x] 3.1 Pas `website/sidebars.js` aan: verwijder verwijzingen naar verwijderde bestanden
- [x] 3.2 Herorden de WayOfWork-sectie zodat de volgorde klopt: intro → organisation → issue-flow → release-process → vacancies
- [x] 3.3 Voeg de ISO-sectie toe aan de sidebar met: intro, quality-policy, security-policy, incident-reporting

## 4. WayOfWork Herschrijven (EN)

- [x] 4.1 Herschrijf `website/docs/WayOfWork/intro.md`: missie, BHAG, vijf kernwaarden, verwijzing naar volledige Intro.md
- [x] 4.2 Voeg `:::caution` admonition toe aan `organisation.md` (outdated / ter managementbeoordeling); voeg verwijzing naar organogram toe
- [x] 4.3 Verwijder dubbele secties in `Issue_flow.md` (bestand bevat de inhoud twee keer); hernoem bestand naar `way-of-work.md` als dat de leesbaarheid ten goede komt
- [x] 4.4 Voeg **Meer lezen**-blok toe aan `release-process.md` met links naar ConductionNL/.github workflows
- [x] 4.5 Verifieer `Vacancies.md` op actualiteit; voeg GitHub-sollicitatieprocedure toe als die ontbreekt

## 5. ISO-Beleidspagina's Aanmaken (EN, draft)

- [x] 5.1 Maak `website/docs/ISO/intro.md` aan: overzicht ISO-certificeringen, verwijzing naar competentievereisten in afgesloten drive
- [x] 5.2 Maak `website/docs/ISO/quality-policy.md` aan met `draft: true` en `:::warning Ter managementbeoordeling`; inhoud: doel, commitment, communicatie (ISO 9001:2015 §5.2)
- [x] 5.3 Maak `website/docs/ISO/security-policy.md` aan met `draft: true` en admonition; inhoud: scope ISMS, beveiligingsdoelstellingen, rollen (ISO 27001:2022 §5.2 + A.5.1)
- [x] 5.4 Maak `website/docs/ISO/incident-reporting.md` aan: meldingskanaal, termijn, onderscheid beveiligingsincident vs. kwaliteitsafwijking (27001 A.6.8 / 9001 §10.2)
- [x] 5.5 Maak een GitHub Issue aan in ConductionNL/.github voor managementbeoordeling van quality-policy.md en security-policy.md

## 6. NL Vertalingen

- [x] 6.1 Maak NL-vertaling van `WayOfWork/intro.md` aan onder `i18n/nl/...`
- [x] 6.2 Maak NL-vertaling van `WayOfWork/organisation.md` aan (met admonition over reviewstatus vertaling)
- [x] 6.3 Maak NL-vertaling van `WayOfWork/way-of-work.md` (issue flow) aan
- [x] 6.4 Maak NL-vertaling van `WayOfWork/release-process.md` aan
- [x] 6.5 Maak NL-vertaling van `WayOfWork/Vacancies.md` aan
- [x] 6.6 Maak NL-vertalingen van alle ISO-pagina's aan (intro, quality-policy, security-policy, incident-reporting)
- [x] 6.7 Maak NL-vertaling van `Products/overview.md` aan

## 7. Build Validatie

- [x] 7.1 Voer `npm install` uit in `website/` (eerste keer na clone)
- [x] 7.2 Voer `npm run build` uit in `website/`; zorg dat er geen broken link errors zijn
- [ ] 7.3 Draai `npm run serve` lokaal en verifieer taal-selector werkt in de browser
- [x] 7.4 Verifieer dat alle ISO-pagina's als draft correct gemarkeerd zijn

## 8. PR en Review

- [ ] 8.1 Commit alle wijzigingen op `feature/hww-2.0`
- [ ] 8.2 Open een PR naar `main` in ConductionNL/.github met beschrijving van wijzigingen
- [ ] 8.3 Voeg reviewers toe en link de management review GitHub Issues
