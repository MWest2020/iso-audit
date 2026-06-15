# Spec — memo-profiles (nieuw)

## ADDED Requirements

### Requirement: Standalone overdraagbare profielen

Een profiel MUST een self-contained YAML-bundle zijn zonder externe pad-refs:
alle styling-, organisatie- en auditor-gegevens staan in het profiel zelf, zodat
het overdraagbaar is naar een andere machine of consultancy-klant.

#### Scenario: Profiel zonder externe refs

- **WHEN** een profiel wordt geladen op een machine zonder de oorspronkelijke assets
- **THEN** rendert de memo volledig, omdat logo, kleuren en font-stack in het profiel zelf staan

### Requirement: Inline SVG-logo met veiligheidsvalidatie

Het logo MUST als inline SVG-string in het profiel staan. De validator MUST een
SVG weigeren die een `<script>`, `<foreignObject>` of externe `<image>`-referentie
bevat.

#### Scenario: Onveilige SVG geweigerd

- **WHEN** een profiel een `logo_svg` met een `<script>`-element bevat
- **THEN** faalt `iso-audit profile validate` met een duidelijke fout en wordt het profiel niet als geldig geaccepteerd

### Requirement: Kleurpalet met afgeleide defaults

Een profiel MUST minimaal `primary` (hex) bevatten. `accent`, `muted`, `border`
en `soft_bg` MUST worden afgeleid van `primary` indien niet expliciet gezet. Alle
kleuren MUST gevalideerd worden als geldige hex.

#### Scenario: Minimaal profiel

- **WHEN** een profiel alleen `primary`, `logo_svg` en organisatienaam bevat
- **THEN** valideert het profiel en worden `accent`/`muted`/`border`/`soft_bg` automatisch afgeleid

#### Scenario: Ongeldige kleur

- **WHEN** `primary` geen geldige hex-waarde is
- **THEN** faalt profiel-validatie met een duidelijke fout

### Requirement: CSS-stack fonts

Een profiel MUST fonts als CSS-stack-string opgeven (default
`-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`),
overschrijfbaar per profiel. Er MUST geen `@font-face` of gevendorde fonts
worden gebruikt.

#### Scenario: Eigen font-stack

- **WHEN** een profiel een eigen `font_stack` opgeeft
- **THEN** gebruikt de gerenderde memo die stack zonder externe font-download

### Requirement: Profiel-locatie en ad-hoc pad

Profielen MUST standaard in `~/.config/iso-audit/profiles/<slug>.yaml` (XDG)
staan. `--profile <path>` MUST ook een absoluut pad accepteren, zonder
path-traversal toe te staan buiten toegestane locaties.

#### Scenario: Ad-hoc profiel via pad

- **WHEN** `--profile /abs/pad/klant.yaml` wordt opgegeven
- **THEN** wordt dat profiel geladen; een pad met traversal-segmenten naar buiten de toegestane scope wordt geweigerd

### Requirement: Profiel-CLI

De tool MUST `iso-audit profile new`, `profile list`, `profile show <slug>` en
`profile validate <slug>` bieden.

#### Scenario: Profielen tonen

- **WHEN** `iso-audit profile list` wordt aangeroepen
- **THEN** worden alle profielen in de XDG-locatie opgesomd met hun slug en organisatienaam

### Requirement: First-run elicitation

`iso-audit profile new` MUST een wizard tonen die organisatienaam, logo-pad
(gelezen → gevalideerd → inline opgenomen), primaire kleur, auditor-naam + rol,
ISO-standaarden in scope, default-taal en het onafhankelijkheid-voorbehoud
uitvraagt en het profiel naar de XDG-locatie opslaat.

#### Scenario: Nieuw profiel aanmaken

- **WHEN** `iso-audit profile new` wordt doorlopen met geldige antwoorden
- **THEN** wordt `~/.config/iso-audit/profiles/<slug>.yaml` aangemaakt met inline SVG-logo en de opgegeven waarden

### Requirement: Profiel schema-versioning

Elk profiel MUST een `schema_version` bevatten. De loader MUST een onbekende
versie weigeren met een heldere migratie-instructie.

#### Scenario: Onbekende schema-versie

- **WHEN** een profiel `schema_version: 2` heeft terwijl de tool alleen v1 kent
- **THEN** weigert de loader het profiel met een melding die uitlegt welke versie wordt verwacht
