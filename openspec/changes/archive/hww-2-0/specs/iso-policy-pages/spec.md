## ADDED Requirements

### Requirement: Kwaliteitsbeleid pagina aanwezig en gemarkeerd als ter review
`website/docs/ISO/quality-policy.md` SHALL aanwezig zijn met de inhoud van het kwaliteitsbeleid (ISO 9001:2015 §5.2). De pagina SHALL `draft: true` in de frontmatter bevatten en een admonition die aangeeft dat het document ter managementbeoordeling ligt.

#### Scenario: Pagina beschikbaar in sidebar
- **WHEN** de Docusaurus-site geladen is
- **THEN** is `ISO / Kwaliteitsbeleid` zichtbaar in de sidebar onder de ISO-sectie

#### Scenario: Draft-markering zichtbaar
- **WHEN** de pagina geopend wordt
- **THEN** bevat de pagina een `:::warning Ter managementbeoordeling` admonition bovenaan

#### Scenario: Verplichte ISO-elementen aanwezig
- **WHEN** de pagina gelezen wordt
- **THEN** bevat ze minimaal: doel van de kwaliteitspolitiek, commitment aan continue verbetering, en hoe het beleid gecommuniceerd wordt aan medewerkers (ISO 9001:2015 §5.2.2)

---

### Requirement: Informatiebeveiligingsbeleid pagina aanwezig en gemarkeerd als ter review
`website/docs/ISO/security-policy.md` SHALL aanwezig zijn met de inhoud van het informatiebeveiligingsbeleid (ISO 27001:2022 §5.2). De pagina SHALL `draft: true` in de frontmatter bevatten en een admonition die aangeeft dat het document ter managementbeoordeling ligt.

#### Scenario: Pagina beschikbaar in sidebar
- **WHEN** de Docusaurus-site geladen is
- **THEN** is `ISO / Informatiebeveiligingsbeleid` zichtbaar in de sidebar

#### Scenario: Verplichte ISO-elementen aanwezig
- **WHEN** de pagina gelezen wordt
- **THEN** bevat ze minimaal: scope van het ISMS, beveiligingsdoelstellingen, rollen voor informatiebeveiliging (ISO 27001:2022 §5.2 + Annex A.5.1)

---

### Requirement: Incidentmeldingsprocedure pagina aanwezig
`website/docs/ISO/incident-reporting.md` SHALL de procedure beschrijven voor het melden van beveiligingsincidenten en bijna-ongelukken (ISO 27001:2022 A.6.8 / ISO 9001:2015 §10.2).

#### Scenario: Meldingskanaal expliciet
- **WHEN** een medewerker de pagina leest
- **THEN** weet die via welk kanaal (e-mail, Slack, GitHub Issue) een incident gemeld moet worden en binnen welke termijn

#### Scenario: Onderscheid incident vs. bijna-ongeluk
- **WHEN** de pagina gelezen wordt
- **THEN** is er een duidelijk onderscheid tussen beveiligingsincidenten (27001 A.6.8) en kwaliteitsafwijkingen / bijna-ongelukken (9001 §10.2)

---

### Requirement: ISO-sectie verwijst naar competentievereisten in afgesloten drive
`website/docs/ISO/intro.md` SHALL een verwijzing bevatten naar de competentievereisten per rol (ISO 9001:2015 §7.2), met de aanduiding dat het gedetailleerde document in de afgesloten drive staat.

#### Scenario: Verwijzing aanwezig zonder inhoud te dupliceren
- **WHEN** een medewerker de ISO-intropagina leest
- **THEN** is er een vermelding dat competentievereisten gedocumenteerd zijn en waar die te vinden zijn, zonder de volledige inhoud over te nemen
