## Why

Het huidige medewerkershandboek ("Hoe We Werken") is verouderd — de eerste 8 pagina's zijn achterhaald en de structuur sluit niet meer aan op hoe Conduction werkt. Tegelijkertijd ontbreekt een publieke, goed vindbare thuisbasis voor onze werkwijze, waarden en bijdragerichtlijnen. Een compact, publiek handboek op docs.conduction.nl lost dit op, dient als basis voor CONTRIBUTING.md/SECURITY.md, en verankert de ISO 9001:2015 + ISO 27001:2022 vereiste gedocumenteerde informatie.

## What Changes

- **i18n**: Docusaurus uitbreiden met NL locale en taal-selector in de navbar (EN blijft default)
- **Content cleanup**: Verwijder stub-bestanden (Market.md, Partners.md, competences.md, knowledge/intro.md), duplicaten (join.md), intern projectmateriaal (Nextcon.md) en reduceer Products/ sectie tot een verwijzing
- **WayOfWork herstructureren**: Compacte HWW-kern van ~5–6 pagina's: Wie we zijn → Hoe we werken → Meer lezen → Meedoen
- **ISO-elementen verankeren**: Kwaliteitsbeleid (9001 §5.2) en Informatiebeveiligingsbeleid (27001 §5.2) expliciet opnemen en klaarzetten voor managementbeoordeling; incidentmeldingsprocedure toevoegen; competentievereisten refereren
- **organisation.md**: Outdated secties flaggen, organogram als leidend markeren (TODO voor managementbeoordeling)
- **NL vertalingen**: Alle WayOfWork-pagina's vertaald via Docusaurus i18n-mappenstructuur (`i18n/nl/docusaurus-plugin-content-docs/`)

## Capabilities

### New Capabilities

- `docusaurus-i18n`: Taal-selector EN/NL in Docusaurus; NL-vertalingen van alle WayOfWork-pagina's
- `hww-core-content`: Geherstructureerde WayOfWork-sectie als compacte HWW-kern (~5–6 pagina's) in EN en NL
- `iso-policy-pages`: Expliciete pagina's voor kwaliteitsbeleid en informatiebeveiligingsbeleid, klaargezet voor managementbeoordeling; incidentmelding procedure
- `content-cleanup`: Verwijdering van stubs, duplicaten en niet-relevante pagina's; Products/-sectie reduceren

### Modified Capabilities

- `handbook-output`: De HWW-outputstructuur wijzigt — van losse Docusaurus-pagina's naar een samenhangende, tweetalige kern met ISO-verankering

## Impact

- `website/docusaurus.config.js` — i18n config, navbar taal-selector
- `website/docs/WayOfWork/` — alle bestanden herschreven/geherstructureerd
- `website/docs/` — stub-bestanden verwijderd, Products/ gereduceerd
- `website/i18n/nl/` — nieuwe map met NL-vertalingen (aangemaakt door Docusaurus i18n)
- Geen wijzigingen aan: root-niveau CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, workflow YAML-bestanden
- Externe afhankelijkheid: ISO-drive (read-only via audit-pipeline) voor ophalen huidige beleidsversies ter review
