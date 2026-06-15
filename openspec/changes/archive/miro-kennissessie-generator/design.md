## Context

De `audit/` module bevat al een werkende Miro-board builder (`miro_board_setup.py`) die frames, stickies en kleuren aanmaakt via de Miro REST API. Die module is echter sterk gekoppeld aan SQLite-data en ISO-auditstructuur. Voor kennissessies willen we hetzelfde API-patroon maar zonder enige DB-dependency: de content komt volledig uit een YAML-bestand.

## Goals / Non-Goals

**Goals:**
- YAML → Miro-bord pipeline, volledig statisch
- Hergebruik van het Miro API-patroon uit `audit/` (rate-limit backoff, auth headers)
- Ondersteuning voor: horizontale tijdlijn, frames per blok, gekleurde stickies per item
- Eerste sessie volledig werkend: Claude Code kennissessie
- Dry-run modus (`--droog`) zodat je content kunt valideren zonder API-calls

**Non-Goals:**
- Geen DB-integratie
- Geen terugschrijven naar of lezen van het Miro-bord (write-only)
- Geen generieke presentatietool — specifiek voor gestructureerde kennissessies
- Geen support voor afbeeldingen of connectors in eerste versie

## Decisions

**D1 — Aparte submodule `sessions/`, geen uitbreiding van `audit/`**
De audit-module heeft eigen DB-logica, clause-maps en domeinkennis. Die koppelen aan sessie-content creëert onnodige afhankelijkheid. Een aparte module is eenvoudiger te testen en te hergebruiken.

**D2 — YAML als content-formaat**
YAML is leesbaar voor niet-developers, versiebeheervriendelijk, en makkelijk uit te breiden. Alternatieven (JSON, Python dict, Google Sheets) zijn minder geschikt voor handmatige contentbewerking.

**D3 — Hergebruik Miro API-hulpfuncties via shared module**
De functies `_headers()`, `_post()`, `maak_frame()`, `maak_sticky()` worden gekopieerd naar `sessions/miro_client.py` (niet geïmporteerd vanuit `audit/` om circulaire dependencies en koppeling te vermijden). Later eventueel te consolideren in een gedeelde lib.

**D4 — Layout: tijdlijn + 2×2 grid**
De tijdlijn bovenaan geeft deelnemers oriëntatie ("waar zijn we nu"). De 2×2 grid maakt de vier blokken gelijkwaardig zichtbaar. Alternatief (lineaire kolommen) past minder goed bij de korte sessieduur en visuele verwachting.

**D5 — Kleurconventie expliciet in YAML**
Elke sticky in de YAML heeft een optioneel `kleur`-veld. Standaardwaarden per bloktype worden ingesteld in de builder. Dit maakt content-aanpassing mogelijk zonder code te wijzigen.

## Risks / Trade-offs

- [Rate limiting Miro API] → Backoff-logica overnemen uit `audit/miro_board_setup.py`; bij grote sessies chunken
- [Content drift] → YAML-bestanden zijn de enige bron van waarheid; geen validatie op volledigheid, dus fouten in YAML leiden pas bij aanmaken bord tot fouten → mitigatie: dry-run modus + YAML-schema validatie (later)
- [Duplicaat API-code] → Bewuste keuze nu; consolideren naar shared lib als derde use case zich aandient
