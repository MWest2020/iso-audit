# Interview-flow zonder Python-automatisme

Het Python-script `iso_audit.miro.interview` is verwijderd in
`openspec/changes/miro-write-trim`. De interview-stap (ongedekte
clausules met de auditor doorlopen) draait nu via **`iso-audit
interview`** in de CLI — geen Miro nodig. Wie tóch een visueel bord
wil, kan dat in twee minuten in Miro neerzetten met onderstaande
prompt.

## Pad A — CLI-interview (aanbevolen)

```bash
uv run iso-audit interview --norm 9001
```

Wat het doet:

1. Leest uit `output/audit.db` welke clausules nog géén match hebben
   (gap-detectie via `clause_matches`-tabel).
2. Loopt per clausule een vraag af in de terminal:
   - `[j]a` → positief
   - `[d]eels` → OFI
   - `[n]ee` → NC
   - `[s]kip` → uitstellen
3. Slaat de antwoorden op in de `interviews`-tabel; pipeline
   consumeert ze automatisch bij de volgende run.

Voor het volledige optie-overzicht: `uv run iso-audit interview --help`.

## Pad B — Miro-bord als visuele variant

Soms wil je de interview-resultaten visueel naast het audit-bord
zien. Maak dan een tweede frame in hetzelfde Miro-bord:

### Miro-AI prompt

```
Voeg aan dit bord een nieuw frame toe rechts naast de bestaande
frames. Naam: "Interview gaps".

Vul het frame met een 3-koloms grid:
- Kolom 1: clausule-id (titel-sticky donkerblauw)
- Kolom 2: vraag aan de auditor (witte sticky, smal)
- Kolom 3: antwoord-zone (leeg, kleuren via legende:
  groen=positief, oranje=OFI, rood=NC)

Maak één rij per onderstaande clausule:
- 4.4: "Worden de processen voor het kwaliteits-/ISMS aantoonbaar
  geborgd en beoordeeld?"
- 5.11: "Hoe wordt offboarding (toegangs-intrekking + activa-
  retournering) aantoonbaar afgesloten?"
- 8.16: "Welke monitoring-baseline bestaat per kritiek platform —
  wat, hoe lang bewaard, wie reviewt?"
- 9.3: "Wanneer en met wie heeft de laatste directiebeoordeling
  plaatsgevonden — wat waren de actiepunten?"
- 10.2: "Hoe worden non-conformiteiten geëvalueerd op effectiviteit
  van de corrigerende maatregel?"

Onder elke rij ruimte voor 1-2 sticky-notes met het antwoord.
```

Vul tijdens het interview de antwoord-stickies handmatig in met de
juiste kleur. De ingest pakt ze net als de bevinding-stickies uit
pad A.

## Welk pad kiezen?

| Situatie | Pad |
|---|---|
| Solo-audit, snelheid prioriteit | A (CLI) |
| Audit met meerdere ISO-eigenaren | B (Miro, gedeeld zichtbaar) |
| Audit waar antwoorden later met MT besproken worden | B (visueel materiaal voor presentatie) |

Pad A schrijft direct naar `output/audit.db`; pad B vereist
expliciet een `iso-audit pipeline --source drive --source miro`-run
om de Miro-antwoorden in te lezen.
