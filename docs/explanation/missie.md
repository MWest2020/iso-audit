---
status: draft
last_reviewed: 2026-07-13
---

# Missie van iso-audit

> **Versie:** 2026-05-06
> **Status:** ankerdocument — wijzigingen via change-proposal in `openspec/changes/`
> **Bron:** afgeleid van het ontwerpdocument `Tool-ontwerp_audit-tool_2026-05-05.md`

Dit document positioneert het tool. Toekomstige Claude-sessies en externe
code-reviewers lezen het om te begrijpen *waarom* iso-audit op de huidige manier
is ontworpen — niet alleen *hoe*.

## Waarom dit tool bestaat

In een organisatie van Conduction's omvang combineert de interne ISO-auditor die
rol typisch met operationele verantwoordelijkheden (team lead, ontwikkelaar,
KAM-coördinator). ISO 19011 §6.4.2 onderkent dit rolconflict expliciet en eist
mitigerende maatregelen wanneer personele scheiding niet realiseerbaar is.

iso-audit is die structurele mitigatie. Niet een efficiency-tool dat de auditor
sneller laat werken, maar een onafhankelijk-functionerend instrument dat
signaleert wanneer de menselijke auditor blinde vlekken heeft of in een patroon
van vooringenomen oordelen zit.

Drie capabilities geven invulling aan die missie. Ze vormen de design-criteria
voor elke change-proposal:

## Capability 1 — Onafhankelijke bronnen

iso-audit haalt audit-bewijsmateriaal uit bron-systemen waar de auditor niet
zelf curatie op uitoefent. Drive met service-account toegang, Jira met
read-only token, MCP-servers, REST-APIs.

**Werking:** bron-configuratie wordt vooraf vastgelegd (env-vars, config-bestand)
en is daarna binnen een audit-run onveranderlijk. Geen runtime `set_folder()`,
`set_filter()` of equivalent — anders kan een operator scope versmallen tijdens
een run en vervalt de onafhankelijkheid.

**Falsifieerbaarheid:** als de auditor dezelfde audit op dezelfde data opnieuw
draait moet het tool dezelfde set documenten zien. Dat is een
contract-test-eis voor elke Source-adapter.

## Capability 2 — Patroondetectie en herhalingsdetectie

iso-audit slaat per bevinding op: input-hash, prompt-versie, model-versie,
raw LLM-output, geparseerde classificatie. Zie het `classifications`-tabel-
ontwerp in de iso-refactor change-proposal.

Dit maakt het mogelijk om patronen over runs heen te detecteren:

- Welke bevindingen komen terug? (recidive — zoals Goya na Sarai)
- Welke documenten worden vaak als "OFI" geklasseerd maar nooit als "NC",
  ondanks NC-trigger-woorden in onderbouwing?
- Welke clausules zijn de auditor consequent permissiever in dan een externe
  certificeerder zou zijn?

**Niet in deze refactor.** De spiegel-laag (capability 3) is een eigen change-
proposal `iso-audit-mirror-foundation` na minimaal vier integer-runs. Deze
refactor zet alleen de hooks (decisions-tabel, classifications-tabel) zodat
later analyse mogelijk wordt — bouwt geen analyse-laag.

## Capability 3 — Auditor-spiegel

iso-audit registreert auditor-besluiten in de `decisions`-tabel: welke
voorstellen werden geaccepteerd, welke afgewezen, welke aangepast, welke
genegeerd. Per beslismoment, per audit-run, met `notifier_naam` zodat
cross-organisatie-vergelijking mogelijk wordt.

Het doel is niet de auditor te vervangen of te beoordelen. Het doel is een
spiegel: een terugkoppeling waar de auditor zelf naar kan kijken om vragen te
stellen als "waarom wijs ik bevindingen van type X consequent af?". ISO 19011
zegt dat de auditor onafhankelijk moet werken; een spiegel maakt
zelfreflectie reproduceerbaar.

**Spec-implicatie.** AutonoomMode persisteert alleen hoog-risico beslissingen —
laag- en midden-risico besluiten in autonoom-runs leveren geen analytische
waarde (voorstel == besluit, geen mens-input). IntegerMode persisteert alle
geescaleerde beslissingen.

## Scope buiten Conduction

Dit tool is ontworpen om buiten Conduction bruikbaar te zijn. Twee design-
keuzes komen daar uit voort:

1. **Notifier-laag pluggable vanaf dag 1.** Slack werkt voor Conduction; voor
   gemeentelijke afnemers (M365/Teams-standaard) of organisaties op andere
   stacks niet. Hard-coded Slack maakt de tool onverkoopbaar zonder rewrite —
   dezelfde valkuil als bij sources, andere laag.
2. **Geen geheime classificatie-logica.** Alle prompts staan in
   `src/iso_audit/classification/prompts/` als versiegestuurde markdown.
   Externe code-review en eventueel open-source-publicatie blijven zo
   mogelijk.

Wanneer een afnemer buiten Conduction het tool gaat gebruiken, splitst er een
`docs/explanation/missie-generic.md` af met de drie capabilities en het
rolconflict-frame los van Conduction-context. Tot die tijd blijft dit document
Conduction-specifiek.

## Wat iso-audit *niet* is

- **Geen pure efficiency-tool.** Snelheid is een bijproduct, geen doel.
  Boring & auditable weegt zwaarder dan een uur sneller klaar zijn.
- **Geen volledige automatisering.** ISO 19011 vereist auditor-oordeel.
  IntegerMode escaleert hoog-risico beslissingen naar de mens; de tool doet
  de admin, niet het oordeel.
- **Geen vervanging voor externe certificeerder.** De externe audit blijft
  een aparte, onafhankelijke evaluatie. iso-audit dient de interne audit-
  cyclus en levert audit-trail die de externe certificeerder *bekijkt*, niet
  *vervangt*.

## Risico's bij het tool zelf

- **Tool-eigenaar wordt single-point-of-failure.** Beperkt mitigeerbaar in
  een organisatie van Conduction's omvang. Geadresseerd door open-source-
  pad, geen geheime logica, externe code-reviews mogelijk via publieke
  repo-structuur. Volledige mitigatie vraagt tweede tool-onderhouder.
- **Tool reproduceert het probleem dat hij wil oplossen.** Als iso-audit zelf
  een blackbox-classifier gebruikt zonder uitleg-keten, dan vervangt hij één
  vorm van vooringenomenheid door een andere. Vandaar capability 2:
  classificatie-output is reproduceerbaar en uitlegbaar.

## Versionering van dit document

Wijzigingen aan deze missie zijn fundamenteel — ze raken alle drie de
capabilities en daarmee elk onderdeel van de codebase. Een wijziging vereist
een eigen change-proposal in `openspec/changes/`, niet alleen een commit op
deze file. Versie-stempel bovenaan dit document wordt bij elke
goedgekeurde wijziging bijgewerkt.
