## Why

Marianne (kwaliteitsmanagement) heeft op 2026-05-04 expliciete feedback gegeven op auditrapport s05 (2026-04-20). Haar oordeel: "AI-gegenereerd zonder goede check, niet voldoende om management daadwerkelijk verbetermaatregelen te laten nemen." Concrete punten:

1. Frame is verkeerd ("de organisatie heeft drie verbetergebieden geïdentificeerd" — bij interne audit is de auditor het subject).
2. Verbeterpunten zijn niet SMART ("mogelijkheden voor verdere formalisering" zegt niets).
3. Inconsistenties (afwijkingenbeheer is tegelijk top-OFI én top-positief) worden niet uitgelegd.
4. ISO-jargon ("extern verstrekte processen", "werkingssituatie") staat letterlijk in de tekst.
5. OFI is niet uitgelegd en niet geaggregeerd — 309 losse items zonder kop.
6. Aanbevelingen bevatten NC-woorden ("onvoldoende", "risico", "ontbreekt") en zijn daarmee verkapte NC's, geen aanbevelingen.

Het rapport moet management *handelingsperspectief* geven. Huidige vorm doet dat niet.

## What Changes

- **Management-summary prompt** (`audit/report_generation.py:_management_summary_prompt`) wordt herzien:
  - Auditor-frame in plaats van organisatie-frame
  - Per top-thema: SMART-blok met *wat geconstateerd*, *concrete actie*, *eigenaar/horizon*
  - Verplichte bridging-zin als clausule zowel >5 OFI's als >5 positieve bevindingen heeft
  - Vertaal-instructie: ISO-clausule-titels niet letterlijk overnemen, gebruik leesbare omschrijving + voorbeelden
  - Verbod op woorden "prominent", "drie kritieke gebieden" als framing
- **Aanbevelingen-template** (`audit/report_generation.py:_top3_aanbevelingen` + handmatige sectie in `pipeline.py`):
  - Format "doe X om Y te bereiken" (positief, vooruitkijkend)
  - Verbod op woorden: *onvoldoende, ontoereikend, risico, lacune, gebrek, ontbreekt* (deze horen bij NC's)
  - Constatering hoort in OFI-sectie, niet in aanbeveling
- **OFI-sectie kop** in markdown-rapport:
  - Definitie van OFI ("kans voor verbetering — geen tekortkoming")
  - Top-5 thema-aggregatie­tabel (thema, aantal, voorgestelde aanpak)
  - Pas dáárna de detail-OFI's
- **Hergeneratie­pad**: nieuwe CLI-flag `--report-only` om rapport opnieuw te genereren uit bestaande bevindingen (DB), zonder volledige re-classificatie. Voor iteratie op tekstwijzigingen zonder LLM-kosten op classificatie-laag.

## Capabilities

### Modified Capabilities

- `report-generation`: Outputstructuur en -toon van management summary, aanbevelingen en OFI-sectie veranderen; uniforme schrijfregels voor management-doelgroep.

### New Capabilities

- `report-regenerate`: Re-render van een bestaand audit-rapport vanuit de bevindingen-DB zonder classificatie-stap. Maakt iteratie op rapport-taal mogelijk zonder LLM-kosten op de hele documentenset.

## Impact

- `audit/report_generation.py` — prompt herschrijven, aanbevelingen-template aanpassen, OFI-kop toevoegen
- `audit/pipeline.py` — nieuwe `--report-only` flag; handmatige aanbevelingen-sectie hergecheckt op verboden woorden
- `audit/local_report.py` — markdown-template krijgt OFI-uitleg-blok bovenaan sectie 3
- Geen wijziging in classificatielaag (`finding_classification.py`, `clause_mapping.py`) — feedback raakt taal, niet bevindingen
- Validatie: na deze change één test-run en handmatige review door Marianne vóór archivering
