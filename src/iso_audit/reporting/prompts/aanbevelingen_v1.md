<!--
Versie-prompt: §3 Aanbevelingen (v1).
SMART + positief + zonder NC-woorden. Dit is waar Marianne's feedback landt:
de aanbevelingen moeten handelingsperspectief geven, geen verkapte NC's zijn.
Een deterministische verboden-woorden-gate in code (_check_verboden_woorden)
controleert de OUTPUT hierna — die gate is de auditeerbare garantie, niet deze prompt.
Placeholders: management_context, aanbevelingen_input.
-->
Schrijf de §3 Aanbevelingen van een interne ISO 9001/27001 auditrapport, in
het Nederlands. Doel: management **handelingsperspectief** geven.

{{management_context}}

PER AANBEVELING (SMART, verplicht):
- (a) WAT is geconstateerd — noem minimaal één concreet document of proces
  uit de bevindingen.
- (b) Een concrete ACTIE die management kan uitvoeren ('doe X om Y te bereiken').
- (c) Een eigenaar (rol) of tijdshorizon (kwartaal/jaar).

VORM:
- Positief geformuleerd: structuur "actie → beoogd resultaat".
- Genummerde lijst, 3 aanbevelingen, elk 2-4 zinnen.
- Concreet, geen vage formuleringen als "mogelijkheden voor verdere
  formalisering en consistentie".

STRIKT VERBODEN — deze woorden mogen NIET voorkomen in de aanbevelingen:
onvoldoende, ontoereikend, risico, lacune, gebrek, ontbreekt. Een
constatering die zo'n woord vereist hoort in de NC- of OFI-sectie, niet hier.
Herformuleer naar de gewenste eindsituatie (bijv. niet "documentatie
ontbreekt" maar "leg de werkwijze vast in X zodat Y aantoonbaar wordt").

Verzin geen leveranciersnamen, tools of personen die niet uit de input volgen.

Te behandelen bevindingen (top-prioriteit NC's, aangevuld met OFI's):
{{aanbevelingen_input}}

Schrijf alleen de genummerde lijst, platte tekst, geen markdown-headers.
