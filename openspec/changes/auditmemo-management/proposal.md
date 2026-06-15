## Why

De gebruikelijke audit-output (detail-rapport, landschap, Excel) mist het
artefact dat het management daadwerkelijk leest: de **één-pager auditmemo**.
Tot nu toe is die memo handmatig in HTML/PDF gemaakt (zie het referentie-
voorbeeld `Auditmemo_management_2026-05-06`). Dat is niet reproduceerbaar, niet
auditeerbaar, en schaalt niet.

De memo moet — net als de overige content — **uit de bestaande findings-dataset
worden gegenereerd**: alleen de NC's en verbeterpunten die een managementbesluit
vragen, met genormeerde citaten, voorbehoud-secties, action-tables en de status
van eerder geconstateerde NC's.

Tegelijk legt deze change de basis voor de transitie ná Marks vertrek: een
**multi-tenant profielsysteem** (Conduction is één profiel; consultancy-klanten
krijgen elk hun eigen) en een **uitbreidbare norm-database** (nu 9001+27001;
later 14001/22301/42001) — zodat de tool overdraagbaar en herbruikbaar is.

Raakt twee van de drie missie-capabilities: het **auditor-spiegel**-frame (de
memo formuleert vanuit de auditor, NC's met dwingende taal, verbeterpunten met
verplichte classificatie-rationale) en **patroondetectie** (cross-clause
positief-vs-OFI-patronen worden in de NC-context expliciet gemaakt).

## What Changes

- **Nieuw `iso-audit memo` subcommand** dat een management-memo (HTML + PDF)
  genereert uit een findings-dataset, een profiel, en een historical-NCs-register.
- **Nieuw profielsysteem** (`iso-audit profile new/list/show/validate`):
  standalone, overdraagbare YAML-bundles met inline SVG-logo, kleurpalet (met
  afgeleide defaults), CSS-stack-fonts, schema-versioning. XDG-locatie
  `~/.config/iso-audit/profiles/<slug>.yaml`; `--profile <path>` voor ad-hoc.
- **Plug-in norm-database** (`data/norms/<slug>.yaml`): genormeerde clausule-
  teksten per taal (NL/EN). Niet hardcoded; ontbrekende clausule = harde fout
  (een memo mag nooit een verzonnen norm-citaat bevatten).
- **Memo-inhoud uit findings**: NC-extractie (`severity == "NC"`),
  verbeterpunt-promotie (drempel of expliciete flag), pattern-detectie,
  voorbehoud-secties, action-tables met visueel gemarkeerde placeholders.
- **Self-contained output**: inline SVG + CSS-fonts → geen externe assets;
  onzichtbare audit-trail-metadata (profile-slug/-versie, tool-versie,
  render-timestamp, findings-dataset-hash) in HTML-comment + PDF-metadata.
- **Architectuur-borging voor later** (niet in MVP-scope, wél in de structuur):
  memo-types, taal-als-data, norm-DB-plug-in, historical-NCs als doorlopend
  cross-audit register. Zie `design.md`.

## Capabilities

### New Capabilities

- `auditmemo` — generatie van de management-memo (HTML + PDF) uit findings +
  norm-DB + profiel, met de vastgelegde memo-structuur.
- `memo-profiles` — multi-tenant profielsysteem (branding, auditor, standaarden,
  taal) als standalone YAML-bundles met validatie.
- `norm-database` — plug-in YAML-norm-database met meertalige clausule-lookup en
  hard-fail bij ontbrekende clausules.

## Scope-grens

MVP: één memo-type (`management-memo`), normen 9001:2015 + 27001:2022, talen
NL + EN. Buiten scope (latere changes): andere memo-types/normen/talen,
Jira/Confluence/Notion-integratie, e-maildistributie, versie-diff,
auto-toewijzing van eigenaren, profiel-schemamigratie.
