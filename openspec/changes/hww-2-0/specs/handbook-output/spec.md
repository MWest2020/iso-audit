## MODIFIED Requirements

### Requirement: Secties verwerken per classificatie
De module SHALL alleen `keep`- en `link-out`-secties opnemen in het nieuwe handboek; `remove`-secties worden weggelaten. **Nieuw**: `link-out`-secties met een WayOfWork-doelstelling SHALL verwijzen naar de corresponderende URL op docs.conduction.nl in plaats van naar een losse externe URL.

#### Scenario: keep-sectie opgenomen
- **WHEN** een sectie classificatie `keep` heeft
- **THEN** wordt de volledige bodytekst opgenomen in het nieuwe doc onder de originele heading

#### Scenario: link-out sectie verwijst naar docs.conduction.nl
- **WHEN** een sectie classificatie `link-out` heeft en het type `way-of-work` draagt
- **THEN** wordt de sectie opgenomen als een kort blok met de heading en een verwijzing naar de corresponderende pagina op `https://docs.conduction.nl/docs/WayOfWork/<pagina>`

#### Scenario: link-out sectie zonder WayOfWork-type
- **WHEN** een sectie classificatie `link-out` heeft zonder type `way-of-work`
- **THEN** wordt de sectie opgenomen met de heading en de oorspronkelijke externe URL (ongewijzigd gedrag)

#### Scenario: remove-sectie weggelaten
- **WHEN** een sectie classificatie `remove` heeft
- **THEN** verschijnt die sectie niet in het nieuwe handboek
