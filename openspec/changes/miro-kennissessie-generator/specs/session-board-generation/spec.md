## ADDED Requirements

### Requirement: Genereer Miro-bord vanuit YAML-sessiedefinitie
Het systeem SHALL een volledig Miro-bord aanmaken op basis van een YAML-bestand met sessie-metadata, blokken en stickies.

#### Scenario: Succesvol bord aanmaken
- **WHEN** de gebruiker `python -m sessions.miro_board_builder --sessie <naam>` uitvoert
- **THEN** maakt het systeem een nieuw Miro-bord aan met de naam uit de YAML, plaatst een horizontale tijdlijn bovenaan, en plaatst per blok een frame in een 2×2 grid

#### Scenario: Onbekende sessie
- **WHEN** de gebruiker een sessienaam opgeeft waarvoor geen YAML-bestand bestaat
- **THEN** stopt het systeem met een duidelijke foutmelding en maakt geen bord aan

### Requirement: Horizontale tijdlijn
Het systeem SHALL een tijdlijn aanmaken bovenaan het bord met één stop per blok, plus een intro-stop.

#### Scenario: Tijdlijn reflecteert sessieblokken
- **WHEN** een sessie 4 blokken heeft
- **THEN** bevat de tijdlijn 5 stops (intro + 4 blokken) als stickies op een horizontale lijn

### Requirement: Frames per blok in 2×2 grid
Het systeem SHALL per blok een frame aanmaken, gepositioneerd in een 2×2 grid onder de tijdlijn.

#### Scenario: Vier blokken worden correct geplaatst
- **WHEN** een sessie 4 blokken heeft
- **THEN** worden frame 1 en 2 op rij 1 geplaatst, frame 3 en 4 op rij 2

#### Scenario: Minder dan vier blokken
- **WHEN** een sessie 2 of 3 blokken heeft
- **THEN** worden frames links-naar-rechts geplaatst zonder lege kolommen te forceren

### Requirement: Gekleurde stickies per item
Het systeem SHALL per item in een blok een sticky aanmaken met de kleur gedefinieerd in de YAML, of een blok-standaardkleur als geen kleur opgegeven is.

#### Scenario: Kleur uit YAML
- **WHEN** een item een `kleur`-veld heeft
- **THEN** gebruikt de sticky die kleur

#### Scenario: Standaardkleur uit blokdefinitie
- **WHEN** een item geen `kleur`-veld heeft en het blok heeft een `standaard_kleur`
- **THEN** gebruikt de sticky de standaardkleur van het blok

### Requirement: Dry-run modus
Het systeem SHALL een `--droog` vlag ondersteunen die de volledige uitvoering simuleert zonder API-calls naar Miro te doen.

#### Scenario: Dry-run produceert geen bord
- **WHEN** de gebruiker `--droog` meegeeft
- **THEN** logt het systeem wat aangemaakt zou worden (bord, frames, stickies) en maakt niets aan in Miro

### Requirement: Rate limit afhandeling
Het systeem SHALL bij een HTTP 429-respons van de Miro API een exponentiële backoff toepassen en de request opnieuw proberen.

#### Scenario: Rate limit bij sticky aanmaken
- **WHEN** de Miro API een 429 teruggeeft
- **THEN** wacht het systeem en herprobeert maximaal 3 keer voor de betreffende request
