## ADDED Requirements

### Requirement: Bevindingen classificeren via Claude
Het systeem SHALL voor elk gekoppeld document-clausule-paar een bevinding genereren en classificeren als NC (non-conformiteit), OFI (kans voor verbetering) of positief.

#### Scenario: Non-conformiteit gedetecteerd
- **WHEN** een document niet voldoet aan de verplichte eisen van een clausule
- **THEN** classificeert het systeem de bevinding als NC en beschrijft de afwijking in het Nederlands

#### Scenario: Kans voor verbetering gedetecteerd
- **WHEN** een document voldoet aan minimale eisen maar verbetermogelijkheden vertoont
- **THEN** classificeert het systeem de bevinding als OFI met een concrete aanbeveling

#### Scenario: Conformiteit vastgesteld
- **WHEN** een document volledig voldoet aan de clausule-eisen
- **THEN** classificeert het systeem de bevinding als positief met een korte onderbouwing

### Requirement: Menselijke review vóór rapportage
Het systeem SHALL alle geclassificeerde bevindingen presenteren voor menselijke review voordat het rapport wordt gegenereerd.

#### Scenario: Reviewstap gepresenteerd
- **WHEN** alle bevindingen zijn geclassificeerd
- **THEN** toont het systeem een overzicht van alle bevindingen met classificatie en vraagt de auditor om bevestiging of correctie

#### Scenario: Auditor corrigeert classificatie
- **WHEN** de auditor een classificatie wijzigt van OFI naar NC
- **THEN** neemt het systeem de gecorrigeerde classificatie over in de rapportage

### Requirement: Bevindingen opslaan in Google Sheets
Het systeem SHALL alle bevindingen (inclusief clausule, document, classificatie, beschrijving) wegschrijven naar een Google Sheets-auditmatrix.

#### Scenario: Bevindingen naar Sheets geschreven
- **WHEN** de classificatiefase is afgerond
- **THEN** bevat het Google Sheets-bestand één rij per bevinding met kolommen: clausule, document, classificatie (NC/OFI/positief), beschrijving, status (open/gesloten)
