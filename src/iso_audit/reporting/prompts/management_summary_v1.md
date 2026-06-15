<!--
Versie-prompt: management summary (v1).
Redactionele regels staan HIER, niet in code. report_generation.py levert
alleen de feiten via {{placeholders}}. Wijzig de toon hier; raak geen Python aan.
Zie ONBOARDING.md en de memory "prompts-versiegestuurd-niet-hardcoded".
Placeholders: management_context, nc_count, ofi_count, pos_count,
top_nc_tekst, top_ofi_tekst, top_pos_tekst, bridging_eis, oordeel_zin.
-->
Schrijf een Nederlandstalige management summary (max 200 woorden) voor een
interne ISO 9001/27001 audit. Doel: feitelijke samenvatting in zakelijke
auditor-taal. KORT — de geprioriteerde acties staan in een aparte §3
Aanbevelingen-tabel die hierna in het rapport komt.

{{management_context}}

FRAME (verplicht):
- De **auditor** is het handelend subject bij verbetergebieden. Schrijf "de
  auditor heeft vastgesteld" of "uit de audit blijkt" — NOOIT "de organisatie
  heeft verbetergebieden geïdentificeerd".

JARGON (verplicht vertalen):
- Neem ISO-clausuletitels niet letterlijk over als ze voor management
  onleesbaar zijn. Vertaal naar een leesbare omschrijving met voorbeelden uit
  Conduction's praktijk. Bijv. "beheersing van extern verstrekte processen"
  → "diensten van derden (hosting, monitoring, leveranciers)".

WAT JE WEL DOET:
- 1 alinea intro: scope + totaalcijfers.
- 1 alinea: in WELKE thema's de verbetergebieden zitten (kort, max 2 zinnen)
  — verwijs voor de details + acties naar §3.
- 1 alinea: positieve bevindingen kort erkennen, concreet.
- 1 zin: bridging als gemengde clusters bestaan (zie hieronder).
- 1 zin: oordeel ('voldoende' / 'onvoldoende').

WAT JE NIET DOET:
- GEEN aparte paragrafen per verbetergebied — die staan in §3.
- GEEN eigenaars, deadlines, RACI, weekplanning, uurschattingen.
- GEEN voorbeeldrijen voor registers/matrices.
- GEEN aanbevelingen ('doe X om Y').
- GEEN risicotaxatie van uitstel.
- GEEN verzonnen leveranciersnamen of personen.

{{bridging_eis}}Resultaatoverzicht:
- Non-conformiteiten (NC): {{nc_count}}
- Kansen voor verbetering (OFI): {{ofi_count}}
- Positieve bevindingen: {{pos_count}}

NC-clusters per clausule:
{{top_nc_tekst}}

OFI-clusters per clausule (top 5):
{{top_ofi_tekst}}

Positieve clusters per clausule (top 5):
{{top_pos_tekst}}

STRUCTUUR (volg precies):
1. Intro (1 alinea): scope + totaalcijfers.
2. Verbetergebieden in 1 alinea, max 2 zinnen: 'De auditor heeft X thema's
   vastgesteld waar verbetering nodig is — voor de geprioriteerde acties zie
   §3 Aanbevelingen.'
3. Positieve bevindingen (1 alinea, concreet, geen loftrompet).
4. Bridging-zin als gemengde clusters bestaan.
5. Oordeel (1 zin) — STRIKT volgens dit sjabloon:
   {{oordeel_zin}}

Schrijf alleen platte tekst, geen markdown-headers.
