## Why

De audit-module genereert al Miro-borden op basis van data, maar er is geen manier om borden te genereren voor interne kennissessies. We willen hetzelfde patroon hergebruiken voor een content-driven pipeline: YAML-definitie in, Miro-bord uit — zonder DB-dependency.

## What Changes

- Nieuwe submodule `sessions/` met een eigen Miro-board builder
- Content-definitie via YAML-bestanden per sessie (statisch, geen DB)
- CLI-commando om een sessie-bord te genereren: `python -m sessions.miro_board_builder --sessie <naam>`
- Eerste sessie-definitie: Claude Code kennissessie voor developers

## Capabilities

### New Capabilities

- `session-board-generation`: Genereer een Miro-bord op basis van een YAML-sessiedefinitie. Ondersteunt frames per blok, gekleurde stickies per item, horizontale tijdlijn, en 2×2 grid-layout.
- `session-content-claude-code`: YAML-definitie van de Claude Code kennissessie: 4 blokken (do's & don'ts, hoe beginnen, 7 levels roadmap, plenair), 30 minuten, doelgroep developers zonder Claude Code ervaring.

### Modified Capabilities

## Impact

- Nieuwe bestanden onder `sessions/` (geen impact op `audit/` of `argocd_sync/`)
- Deelt `MIRO_API_TOKEN` uit `.env` met de audit-module
- Geen nieuwe externe dependencies buiten `requests` (al aanwezig)
