# Spec — report-generation (gewijzigd)

## ADDED Requirements

### Requirement: Management summary auditor-frame

De management summary MOET de auditor als handelend subject gebruiken bij het benoemen van verbetergebieden. Formuleringen waarin "de organisatie [verbetergebieden] heeft geïdentificeerd" zijn verboden in de samenvatting van een interne audit.

#### Scenario: Top-thema's worden door de auditor benoemd

- **WHEN** de management summary de top-N OFI-thema's benoemt
- **THEN** wordt het subject "de auditor" (of equivalent: "uit de audit blijkt") gebruikt
- **AND** worden geen frasen gebruikt als "de organisatie heeft drie verbetergebieden geïdentificeerd"

### Requirement: SMART-formulering per top-thema

> **Ontwerpbesluit 2026-06-15:** de SMART-elementen staan in de **§3
> Aanbevelingen**-sectie, niet in de management summary zelf. De summary blijft
> kort en verwijst naar §3 (auditor-frame). Dit dient Marianne's intentie
> (handelingsperspectief) beter dan SMART-blokken in de samenvatting proppen.
> "Top-thema" hieronder = een rij in de §3 Aanbevelingen-tabel.

Voor elk top-thema in de §3 Aanbevelingen MOET de tekst expliciet aangeven: (a) wat is geconstateerd inclusief specifieke documenten/processen, (b) welke concrete actie wordt voorgesteld, (c) eigenaar of tijdshorizon (kwartaal/jaar). Vage formuleringen ("mogelijkheden voor verdere formalisering en consistentie") zijn niet voldoende.

#### Scenario: Thema-blok bevat alle drie SMART-elementen

- **WHEN** een top-thema wordt beschreven in de samenvatting
- **THEN** noemt de tekst minimaal één concreet document of proces uit de bevindingen
- **AND** geeft de tekst een actiestap die uitvoerbaar is door management
- **AND** noemt de tekst een eigenaar (rol) of tijdshorizon

### Requirement: Bridging bij gemengde clusters

Wanneer een ISO-clausule zowel meer dan 5 OFI's als meer dan 5 positieve bevindingen heeft, MOET de management summary expliciet uitleggen waarom deze observaties samen kunnen gaan (bv. uitvoering werkt, vastlegging is gefragmenteerd). Een louter naast-elkaar-zetten van "verbeterpunt" en "sterk punt" voor dezelfde clausule is niet toegestaan.

#### Scenario: Clausule 10.2 met 20 OFI's en 11 positieve bevindingen

- **WHEN** clausule 10.2 in beide top-lijsten staat
- **THEN** bevat de samenvatting een bridging-zin die het verschil tussen uitvoering en vastlegging toelicht

### Requirement: Jargon vertaling

ISO-clausule-titels MOGEN NIET letterlijk in de lopende tekst van de management summary verschijnen wanneer ze voor management onleesbaar zijn. Ze moeten worden vertaald naar omschrijvingen met voorbeelden uit Conduction's praktijk.

#### Scenario: Clausule 8.16 in samenvatting

- **WHEN** clausule 8.16 ("Beheersing van extern verstrekte processen, producten en diensten") wordt benoemd
- **THEN** gebruikt de tekst een omschrijving als "diensten van derden (hosting, monitoring, leveranciers)"
- **AND** verschijnt "extern verstrekte processen" niet als hoofdterm in de samenvatting

### Requirement: OFI-uitleg en aggregatie

De OFI-sectie van het rapport MOET aan het begin een definitie van OFI bevatten en een top-5 thema-aggregatie­tabel met (thema, aantal, voorgestelde aanpak). Pas daarna mogen detail-items volgen.

#### Scenario: Rapport bevat OFI-sectie

- **WHEN** sectie "Bevindingen" of "OFI" wordt gerenderd
- **THEN** staat bovenaan een definitie ("OFI = Opportunity For Improvement / kans voor verbetering — geen tekortkoming")
- **AND** staat eronder een tabel met de top-5 thema's, aantallen en voorgestelde aanpak
- **AND** volgen de detail-items pas na deze samenvatting

### Requirement: Aanbevelingen-template zonder NC-woorden

Aanbevelingen MOETEN positief geformuleerd zijn ("doe X om Y te bereiken"). De woorden *onvoldoende, ontoereikend, risico, lacune, gebrek, ontbreekt* MOGEN NIET voorkomen in de aanbevelingen-sectie. Constateringen die deze woorden vereisen horen thuis in de NC- of OFI-sectie, niet in de aanbeveling.

#### Scenario: Aanbevelingen-sectie wordt gerenderd

- **WHEN** een aanbeveling wordt geformuleerd
- **THEN** bevat de tekst geen van de verboden woorden
- **AND** is de structuur "actie → beoogd resultaat" herkenbaar

#### Scenario: Geautomatiseerde validatie

- **WHEN** het rapport wordt gegenereerd
- **THEN** controleert een nacheck-functie de aanbevelingen-sectie op verboden woorden
- **AND** logt een waarschuwing wanneer een verboden woord wordt gedetecteerd

### Requirement: Report-only hergeneratie

De pipeline MOET een modus ondersteunen waarin het rapport opnieuw wordt gegenereerd vanuit de bestaande bevindingen-DB, zonder de classificatiestap (LLM-calls) opnieuw uit te voeren. Doel: iteratie op rapporttaal zonder kosten op de classificatielaag.

#### Scenario: pipeline draait met --report-only

- **WHEN** de pipeline wordt aangeroepen met `--report-only`
- **THEN** worden bevindingen geladen uit `output/audit_*.db`
- **AND** wordt alleen `_genereer_management_summary` + `schrijf_rapport` uitgevoerd
- **AND** worden Drive/Miro/Sheets-stappen overgeslagen
