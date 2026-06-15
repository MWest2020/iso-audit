## 1. Modulestructuur

- [x] 1.1 Maak `sessions/` directory aan met `__init__.py`
- [x] 1.2 Maak `sessions/content/` directory aan voor YAML-bestanden
- [x] 1.3 Voeg `sessions/` toe aan `.gitignore`-uitzonderingen (inhoud mag gecommit worden)

## 2. Miro API client

- [x] 2.1 Maak `sessions/miro_client.py` met `_headers()`, `_post()`, `maak_bord()`, `maak_frame()`, `maak_sticky()` (gebaseerd op `audit/miro_board_setup.py`)
- [x] 2.2 Implementeer rate-limit backoff (HTTP 429 → exponentieel, max 3 pogingen)
- [x] 2.3 Implementeer dry-run modus: log acties zonder API-calls te doen

## 3. Board builder

- [x] 3.1 Maak `sessions/miro_board_builder.py` met CLI-entry (`--sessie`, `--droog`, `--bord-id`)
- [x] 3.2 Implementeer YAML-loader: laad `sessions/content/<naam>.yaml`, valideer verplichte velden
- [x] 3.3 Implementeer tijdlijn-generator: 5 horizontale stickies (intro + 4 blokken)
- [x] 3.4 Implementeer frame-plaatsing in 2×2 grid met juiste x/y-offsets
- [x] 3.5 Implementeer sticky-plaatsing per blok: kleur uit item of standaard_kleur uit blok
- [x] 3.6 Voeg foutafhandeling toe voor ontbrekende sessie-YAML

## 4. Sessie-content Claude Code

- [x] 4.1 Maak `sessions/content/claude_code_kennissessie.yaml` aan met sessie-metadata (naam, duur, doelgroep)
- [x] 4.2 Vul blok 1: do's (groen) en don'ts (rood) voor developers zonder Claude Code ervaring
- [x] 4.3 Vul blok 2: stap-voor-stap hoe beginnen (blauw) + concreet voorbeeld (geel)
- [x] 4.4 Vul blok 3: 7 levels roadmap, levels 1-3 onderscheiden als "in scope voor beginners"
- [x] 4.5 Vul blok 4: 2 open discussievragen (geel) + 3 lege input-stickies (lichtgrijs)

## 5. Verificatie

- [x] 5.1 Dry-run uitvoeren op claude_code_kennissessie: output logregels controleren
- [ ] 5.2 Live run uitvoeren: bord aanmaken en visueel verifiëren in Miro
- [ ] 5.3 Controleer dat tijdlijn, frames en stickies correct gepositioneerd zijn
