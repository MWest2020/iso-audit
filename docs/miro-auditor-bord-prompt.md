# Miro auditor-bord opzetten via Miro-AI

Het Python-script dat een Miro-audit-bord automatisch opzette
(`iso_audit.miro.board_setup`) is verwijderd in
`openspec/changes/miro-write-trim`. Miro's ingebouwde AI doet dit
sneller én met betere layout-controle. Deze pagina beschrijft hoe je
in twee minuten een werkbaar audit-bord neerzet, en hoe je 'm
verbindt met de iso-audit pipeline.

## Stap 1 — Open Miro en start een leeg bord

Maak een nieuw bord in je Conduction-workspace. Geef het een naam
volgens de conventie `iso-audit-{norm}-{audit-datum}`, bijvoorbeeld
`iso-audit-9001-2026-Q2`.

## Stap 2 — Open Miro-AI

Klik op het AI-icoon (sterretje) in de toolbar of gebruik de
shortcut `Cmd/Ctrl + I`. Plak deze prompt:

```
Maak een audit-bord voor ISO 9001 + ISO 27001 met:

- 5 frames horizontaal naast elkaar, elk met titel:
  1. Context (clausule 4)
  2. Leiderschap (clausule 5)
  3. Planning (clausule 6)
  4. Ondersteuning + Uitvoering (clausules 7-8)
  5. Evaluatie + Verbetering (clausules 9-10)

- Boven elk frame: een titel-sticky in donkerblauw met
  witte tekst.

- Onder de frames een legende-strook van 4 sticky-notes:
  - Groen:  "positief — voldoet aantoonbaar"
  - Oranje: "OFI — kans tot verbetering"
  - Rood:   "NC — non-conformiteit"
  - Geel:   "vraag — onduidelijk, opvolging nodig"

- Frame-formaat: 800 x 1200 px. Onderlinge spacing 100 px.

Voeg geen sticky-notes binnen de frames toe — die plaatst de
auditor handmatig tijdens documentanalyse.
```

Klik **Genereer**. Pas indien nodig aan (drag-and-drop, formaat,
kleuren). De AI maakt de basis-layout zoals beschreven.

## Stap 3 — Kopieer de board-ID

De Miro-URL is van de vorm:

```
https://miro.com/app/board/<BOARD_ID>/
```

De `<BOARD_ID>` is het stuk tussen `/board/` en de volgende `/`.

## Stap 4 — Configureer in `.env`

```bash
export MIRO_BOARD_ID=<de gekopieerde ID>
export MIRO_API_TOKEN=<je Miro API token met boards:read>
```

Of voeg ze toe aan `.env` in de iso-audit repo. Token genereer je in
Miro Dashboard → Profile → Apps → Create new app → OAuth scopes →
`boards:read`.

## Stap 5 — Tijdens de audit

Tijdens documentanalyse plak je per bevinding een sticky-note in
het juiste frame:

- **Kleur** = pre-classificatie (groen / oranje / rood);
- **Tekst** = korte bevinding, eventueel beginnend met de clausule-id
  (`5.11:` of `6.2:`) zodat de ingest die kan herkennen.

Voorbeeld stickies:

- groen: `5.11: offboarding-procedure aanwezig en consequent toegepast`
- oranje: `9.3: directiebeoordeling minder frequent dan bedoeld`
- rood: `8.16: monitoring-baseline ontbreekt op kritieke services`

## Stap 6 — Pipeline aanroepen

Wanneer de audit klaar is:

```bash
uv run iso-audit pipeline --source drive --source miro \
    --norm beide --mode autonoom
```

De `miro`-source leest alle sticky-notes via `haal_notities_op`,
maps kleur → pre-classificatie, koppelt aan clausules op basis van
de `<id>:`-prefix in de tekst, en voegt ze samen met de Drive-
bevindingen via `merge_met_drive_bevindingen`.

## Waarom dit pad — niet het oude Python-script?

- **Real-time layout-controle.** Miro-AI past frames en stickies
  visueel aan op basis van je feedback; ons Python-script moest dat
  vooraf berekenen.
- **Geen Miro-API-quota verbruik** voor write-operaties tijdens
  bord-setup.
- **Geen onderhoud** op frame-positionering, sticky-kleur-codes,
  rate-limiting voor batch-create — dat veranderde regelmatig in
  Miro's API.
- **De ISO-pipeline gebruikt alleen READ.** Auto-creëren was
  comfort, geen capability uit `docs/missie.md`.

## Veiligheid

Zorg dat het bord alleen gedeeld is met auditoren + ISO-eigenaren.
Een Miro-bord met klant-bevindingen valt onder 27001 §5.12
(informatieclassificatie) — behandel als "Intern" of strenger.
