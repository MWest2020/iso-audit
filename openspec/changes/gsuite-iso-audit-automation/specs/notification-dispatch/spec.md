## ADDED Requirements

### Requirement: Audit-uitnodigingen versturen via Google Calendar
Het systeem SHALL, indien geconfigureerd, een Google Calendar-uitnodiging aanmaken voor de auditafspraak met relevante deelnemers en een link naar het auditrapport in de beschrijving.

#### Scenario: Calendar-uitnodiging aangemaakt
- **WHEN** de planningsstap wordt uitgevoerd met een datum, tijd en deelnemerslijst
- **THEN** verschijnt er een Google Calendar-event met titel, datum/tijd, deelnemers en een Drive-link naar het rapport in de omschrijving

#### Scenario: Geen deelnemers geconfigureerd
- **WHEN** de deelnemerslijst leeg is
- **THEN** slaat het systeem de Calendar-stap over en logt "calendar-uitnodiging overgeslagen: geen deelnemers geconfigureerd"

### Requirement: Auditrapport optioneel versturen via Gmail
Het systeem SHALL, indien geconfigureerd, het auditrapport en de Slides-samenvatting als Drive-links versturen via Gmail aan een configureerbare lijst ontvangers.

#### Scenario: Verzending uitgevoerd
- **WHEN** de Gmail-notificatiestap wordt uitgevoerd met een niet-lege ontvangerslijst
- **THEN** ontvangen alle geconfigureerde ontvangers een e-mail met het rapport en de presentatie als Drive-links (niet als bijlage)

#### Scenario: Lege ontvangerslijst
- **WHEN** de ontvangerslijst leeg is of niet is geconfigureerd
- **THEN** slaat het systeem de Gmail-stap over en logt "gmail-notificatie overgeslagen: geen ontvangers geconfigureerd"

### Requirement: E-mailinhoud in het Nederlands
De e-mail SHALL een Nederlandstalige begeleidende tekst bevatten met: audittype, uitvoeringsdatum, aantal NC's en een directe link naar het rapport.

#### Scenario: E-mailinhoud correct
- **WHEN** een e-mail wordt verstuurd
- **THEN** bevat de begeleidende tekst: norm, datum, aantal NC's, aantal OFI's en een klikbare Drive-link naar het rapport

### Requirement: Alle verzendacties vereisen expliciete bevestiging
Het systeem SHALL vóór elke verzendactie (Calendar én Gmail) de auditor om expliciete bevestiging vragen.

#### Scenario: Bevestigingsvraag gesteld
- **WHEN** een verzendstap wordt bereikt
- **THEN** toont het systeem de ontvangers/deelnemers en vraagt "Bevestig verzending (ja/nee)" voordat de actie wordt uitgevoerd
