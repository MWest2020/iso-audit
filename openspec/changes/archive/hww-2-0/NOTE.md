# Gearchiveerd — buiten scope iso-audit (2026-06-15)

Deze change gaat volledig over de **Docusaurus-website** (`docs.conduction.nl`):
i18n EN/NL, herstructurering van de WayOfWork-pagina's, ISO-beleidspagina's,
content-cleanup. Dat is werk in de repo **`ConductionNL/.github`** (de
`website/`-Docusaurus-site), niet in `iso-audit`.

De change is hier beland bij de verhuizing van OpenSpec-changes uit
`Ops_to_Biz` (commit `4ffc07f`). Hij is hierheen verplaatst om de audit-trail
te bewaren, maar hoort thuis in de website-repo en wordt daar afgemaakt.

**Openstaande tasks** (in `tasks.md`, niet afgevinkt) horen bij die andere
repo: `npm run serve` + browsercheck (7.3), commit op `feature/hww-2.0` (8.1),
PR naar `main` in `ConductionNL/.github` (8.2), reviewers/issues (8.3).

Idee voor later (door Mark genoemd, 2026-06-15): de HWW-website zou naar de
*output* van de iso-audit-tool kunnen kijken — maar dat is een toekomstige
integratie, geen onderdeel van deze change.
