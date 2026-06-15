"""ISO 9001:2015 normteksten — gemigreerd uit Ops_to_Biz/audit/normteksten.py.

Schema per clausule-key:
  - normtekst     — letterlijke (verkorte) eis uit de norm, in Nederlands
  - interpretatie — praktische uitleg voor een manager
  - bewijslast    — concrete documenten/artefacten die een externe auditor verwacht
  - sub_punten    — optioneel: lijst met sub-clausule-blokken

YAML-migratie van deze data blijft een aparte change na milestone C; voor
nu is een Python-dict de eenvoudigste en meest doorzoekbare vorm.
"""

from __future__ import annotations

from typing import Any

NORMTEKSTEN_9001: dict[str, dict[str, Any]] = {
    "4.1": {
        "normtekst": (
            "De organisatie moet de externe en interne aangelegenheden bepalen "
            "die relevant zijn voor haar doel en strategische richting en die "
            "van invloed zijn op haar vermogen om de beoogde resultaten van het "
            "kwaliteitsmanagementsysteem te behalen."
        ),
        "interpretatie": (
            "Je moet weten in welke omgeving je opereert voordat je processen "
            "kunt inrichten. Interne factoren zijn cultuur, capaciteit en "
            "systemen; externe factoren zijn markt, wet- en regelgeving en "
            "concurrentie. Zonder dit inzicht is elk kwaliteitsplan gebouwd op "
            "aannames."
        ),
        "bewijslast": [
            "Contextanalyse (SWOT, PESTEL of vergelijkbaar document)",
            "Notulen directiebeoordeling waarin context is besproken",
            "Strategisch plan of beleidsverklaring met verwijzing naar context",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Externe aangelegenheden bepaald (markt, wet/regelgeving, concurrentie, technologie)",
                "bewijslast": [
                    "PESTEL of marktanalyse met datum",
                    "Vermelding in directiebeoordeling of strategie-document",
                ],
            },
            {
                "id": "b",
                "eis": "Interne aangelegenheden bepaald (cultuur, capaciteit, kennis, systemen, waarden)",
                "bewijslast": [
                    "SWOT of interne analyse opgenomen in contextdocument",
                    "Bewijs dat interne factoren de KMS-scope beïnvloeden",
                ],
            },
        ],
    },
    "4.2": {
        "normtekst": (
            "De organisatie moet de relevante belanghebbenden bepalen en hun "
            "relevante eisen voor het kwaliteitsmanagementsysteem vaststellen. "
            "Deze informatie moet worden gemonitord en beoordeeld."
        ),
        "interpretatie": (
            "Klanten, medewerkers, leveranciers en toezichthouders hebben elk "
            "eigen verwachtingen. Door deze expliciet te maken voorkom je "
            "verrassingen en kun je gericht sturen. Een auditor wil zien dat "
            "je dit structureel bijhoudt, niet eenmalig."
        ),
        "bewijslast": [
            "Stakeholderregister met eisen per belanghebbende",
            "Bewijs van periodieke herziening (notulen, versiedatum)",
            "Koppeling tussen stakeholdereisen en KMS-scope of -doelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Relevante belanghebbenden geïdentificeerd (klanten, medewerkers, partners, toezichthouders, aandeelhouders)",
                "bewijslast": [
                    "Stakeholderregister met naam/groep en rol t.o.v. KMS",
                    "Voor Conduction: klanten, developers, partners (SIM/Procura), NEN/certificeringsinstantie",
                ],
            },
            {
                "id": "b",
                "eis": "Relevante eisen per belanghebbende vastgesteld (contractueel, wettelijk, impliciet)",
                "bewijslast": [
                    "Eisen per stakeholder gedocumenteerd (SLA, AVG, kwaliteitsverwachtingen)",
                    "Koppeling eisen aan KMS-scope of procesafspraken",
                ],
            },
            {
                "id": "c",
                "eis": "Informatie over belanghebbenden en hun eisen periodiek gemonitord en herzien",
                "bewijslast": [
                    "Versiedatum stakeholderregister of aantekening in directiebeoordeling",
                    "Bewijs van review bij contractwijziging of nieuwe klant",
                ],
            },
        ],
    },
    "4.3": {
        "normtekst": (
            "De organisatie moet de grenzen en toepasselijkheid van het "
            "kwaliteitsmanagementsysteem bepalen om de scope vast te stellen. "
            "De scope moet beschikbaar zijn als gedocumenteerde informatie."
        ),
        "interpretatie": (
            "De scope geeft aan welke onderdelen van de organisatie onder het "
            "certificaat vallen. Een te brede scope zonder dekking is net zo "
            "problematisch als een te enge scope die klanten misleidt. De "
            "redenering voor uitsluitingen moet aantoonbaar zijn."
        ),
        "bewijslast": [
            "Scopedocument (gedocumenteerde informatie)",
            "Motivatie voor eventuele uitsluitingen van clausules",
            "Certificaat of aanvraagdossier met scopeomschrijving",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Context (4.1) en stakeholdereisen (4.2) zijn meegenomen bij scopebepaling",
                "bewijslast": [
                    "Scopedocument verwijst naar contextanalyse en stakeholderregister",
                ],
            },
            {
                "id": "b",
                "eis": "Activiteiten, producten en diensten van de organisatie zijn beschreven",
                "bewijslast": [
                    "Scopeomschrijving in kwaliteitshandboek of certificaatdossier",
                ],
            },
            {
                "id": "c",
                "eis": "Eventuele uitsluitingen zijn gemotiveerd en beperkt tot clausules zonder invloed op conformiteit",
                "bewijslast": [
                    "Uitsluitingentabel met per clausule de motivatie (bijv. 8.3 indien geen O&O)",
                ],
            },
        ],
    },
    "4.4": {
        "normtekst": (
            "De organisatie moet de processen die nodig zijn voor het "
            "kwaliteitsmanagementsysteem en hun onderlinge samenhang bepalen, "
            "implementeren, onderhouden en continu verbeteren."
        ),
        "interpretatie": (
            "Het KMS is geen map met procedures; het is een samenhangend "
            "systeem van processen. Je moet weten welke inputs en outputs elk "
            "proces heeft, wie verantwoordelijk is en hoe processen op elkaar "
            "inwerken. Dit is de ruggengraat van de ISO 9001-aanpak."
        ),
        "bewijslast": [
            "Proceslandkaart of schildpad-diagram per kernproces",
            "Procesbeschrijvingen met inputs, outputs, eigenaar en KPI's",
            "Bewijs van procesmonitoring (metingen, dashboards)",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Processen bepaald: inputs, outputs, volgorde en wisselwerking",
                "bewijslast": [
                    "Proceslandkaart met alle KMS-processen en hun relaties",
                ],
            },
            {
                "id": "b",
                "eis": "Criteria, methoden en KPI's per proces vastgesteld",
                "bewijslast": [
                    "Procesbeschrijving of schildpad-diagram met meting en norm",
                ],
            },
            {
                "id": "c",
                "eis": "Verantwoordelijkheden en bevoegdheden per proces belegd",
                "bewijslast": [
                    "RACI of proceseigenaar per proces gedocumenteerd",
                ],
            },
            {
                "id": "d",
                "eis": "Risico's en kansen per proces geïdentificeerd (link naar 6.1)",
                "bewijslast": [
                    "Risicoregister of risicokolom in procesbeschrijving",
                ],
            },
            {
                "id": "e",
                "eis": "Processen continu verbeterd; gedocumenteerde informatie bewaard",
                "bewijslast": [
                    "Verbeterregister of versiehistorie van procesbeschrijvingen",
                ],
            },
        ],
    },
    "5.1": {
        "normtekst": (
            "Het topmanagement moet blijk geven van leiderschap en betrokkenheid "
            "bij het kwaliteitsmanagementsysteem door verantwoordelijkheid te "
            "nemen voor de effectiviteit ervan en kwaliteitsbeleid en "
            "-doelstellingen vast te stellen."
        ),
        "interpretatie": (
            "ISO 9001 verschoof verantwoordelijkheid bewust van de "
            "kwaliteitsmanager naar de directie. Als de directeur niet actief "
            "betrokken is, blijft kwaliteit een afdeling in plaats van een "
            "organisatiebrede cultuur. Een auditor toetst dit aan concrete "
            "acties, niet aan mooie woorden."
        ),
        "bewijslast": [
            "Notulen directiebeoordeling ondertekend door topmanagement",
            "Kwaliteitsbeleid ondertekend door directie",
            "Aantoonbare deelname van directie aan audits of verbeterprojecten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Directie is eindverantwoordelijk voor KMS-effectiviteit (niet gedelegeerd aan kwaliteitsfunctionaris)",
                "bewijslast": [
                    "Notulen of actiepunten directie met expliciete KMS-betrokkenheid",
                ],
            },
            {
                "id": "b",
                "eis": "Kwaliteitsbeleid en doelstellingen afgestemd op strategische richting",
                "bewijslast": [
                    "Kwaliteitsbeleid ondertekend door directie, verwijzing naar strategie",
                ],
            },
            {
                "id": "c",
                "eis": "KMS geïntegreerd in bedrijfsprocessen (niet een los kwaliteitssysteem)",
                "bewijslast": [
                    "Bewijs dat KMS-eisen zijn opgenomen in werkprocessen (sprint, delivery)",
                ],
            },
            {
                "id": "d",
                "eis": "Klantgerichtheid geborgd: klanteisen en compliance worden bewaakt",
                "bewijslast": [
                    "Klanttevredenheidsmeting of klachtenregister met opvolging door directie",
                ],
            },
        ],
    },
    "5.2": {
        "normtekst": (
            "Het topmanagement moet een kwaliteitsbeleid vaststellen, "
            "implementeren en onderhouden dat passend is voor de context van "
            "de organisatie en een kader biedt voor kwaliteitsdoelstellingen."
        ),
        "interpretatie": (
            "Het kwaliteitsbeleid is de publieke belofte van de directie over "
            "wat kwaliteit voor de organisatie betekent. Het moet meer zijn dan "
            "een poster op de muur: medewerkers moeten het kennen en begrijpen, "
            "en het moet aantoonbaar doorwerken in doelstellingen."
        ),
        "bewijslast": [
            "Ondertekend kwaliteitsbeleid (gedocumenteerde informatie)",
            "Bewijs van communicatie aan medewerkers (intranet, toolbox, e-mail)",
            "Koppeling tussen beleid en meetbare kwaliteitsdoelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Kwaliteitsbeleid past bij de context en richting van de organisatie",
                "bewijslast": [
                    "Beleidstekst verwijst naar dienstverlening Conduction en klantfocus",
                ],
            },
            {
                "id": "b",
                "eis": "Beleid biedt kader voor meetbare kwaliteitsdoelstellingen",
                "bewijslast": [
                    "Aantoonbare link: beleidsstatement → concrete KPI of doelstelling",
                ],
            },
            {
                "id": "c",
                "eis": "Beleid bevat toezegging voor naleving van eisen én continue verbetering",
                "bewijslast": [
                    "Beleidstekst bevat expliciete verbeteringsclausule",
                ],
            },
            {
                "id": "d",
                "eis": "Beleid is gedocumenteerd, gecommuniceerd, begrepen en beschikbaar voor stakeholders",
                "bewijslast": [
                    "Versiedatum beleid, bewijs van communicatie (email/intranet), toegankelijk voor klanten op aanvraag",
                ],
            },
        ],
    },
    "5.3": {
        "normtekst": (
            "Het topmanagement moet de verantwoordelijkheden en bevoegdheden "
            "voor relevante rollen toewijzen, communiceren en begrijpelijk maken "
            "binnen de organisatie."
        ),
        "interpretatie": (
            "Onduidelijke verantwoordelijkheden zijn de meest voorkomende "
            "oorzaak van kwaliteitsproblemen. Iedereen moet weten wat zijn rol "
            "in het KMS is. Dit geldt speciaal voor de persoon die rapporteert "
            "aan topmanagement over KMS-prestaties."
        ),
        "bewijslast": [
            "Organogram met KMS-gerelateerde rollen",
            "Functiebeschrijvingen met expliciete KMS-verantwoordelijkheden",
            "Benoemingsbesluit of aanwijzingsbrief voor KMS-verantwoordelijke",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "KMS-rollen zijn toegewezen aan specifieke personen en gecommuniceerd",
                "bewijslast": [
                    "Organogram of RACI met KMS-verantwoordelijke, proceseigenaren",
                ],
            },
            {
                "id": "b",
                "eis": "KMS-verantwoordelijke rapporteert aan topmanagement over KMS-prestaties",
                "bewijslast": [
                    "Bewijs van rapportage: presentatie, memo of agenda directiebeoordeling",
                ],
            },
            {
                "id": "c",
                "eis": "Klantgerichtheid actief bevorderd door bevoegde personen",
                "bewijslast": [
                    "Functiebeschrijving met klantfocusverantwoordelijkheid (bijv. accountmanager, delivery lead)",
                ],
            },
        ],
    },
    "6.1": {
        "normtekst": (
            "De organisatie moet risico's en kansen bepalen die aangepakt moeten "
            "worden om te waarborgen dat het KMS de beoogde resultaten kan "
            "behalen, ongewenste effecten voorkomt en continue verbetering "
            "bewerkstelligt."
        ),
        "interpretatie": (
            "Risicomanagement in ISO 9001 is pragmatisch: je hoeft geen formeel "
            "risicoregister te hebben, maar je moet aantonen dat je nadenkt over "
            "wat mis kan gaan en wat je kansen zijn. Acties die je neemt moeten "
            "proportioneel zijn aan het risico."
        ),
        "bewijslast": [
            "Risicoregister of SWOT met risico's en kansen",
            "Actieplannen gekoppeld aan geïdentificeerde risico's",
            "Bewijs van evaluatie van de effectiviteit van maatregelen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Risico's en kansen bepaald vanuit context (4.1) en stakeholders (4.2)",
                "bewijslast": [
                    "Risicoregister of SWOT met verwijzing naar contextanalyse en stakeholderregister",
                ],
            },
            {
                "id": "b",
                "eis": "Acties gepland om risico's te beheersen en kansen te benutten",
                "bewijslast": [
                    "Actieplan per risico: maatregel, eigenaar, deadline",
                ],
            },
            {
                "id": "c",
                "eis": "Maatregelen geïntegreerd in KMS-processen en effectiviteit beoordeeld",
                "bewijslast": [
                    "Bewijs van periodieke risicoreview (directiebeoordeling of risicoaudit)",
                ],
            },
        ],
    },
    "6.2": {
        "normtekst": (
            "De organisatie moet kwaliteitsdoelstellingen vaststellen voor "
            "relevante functies, niveaus en processen. Doelstellingen moeten "
            "meetbaar zijn, worden gemonitord en worden gecommuniceerd."
        ),
        "interpretatie": (
            "Doelstellingen maken het kwaliteitsbeleid concreet en meetbaar. "
            "Zonder SMART-doelstellingen is er geen manier om te weten of het "
            "KMS werkt. Ze moeten ook echt worden bijgehouden, niet alleen "
            "jaarlijks worden opgeschreven."
        ),
        "bewijslast": [
            "Overzicht kwaliteitsdoelstellingen per afdeling of proces",
            "KPI-dashboard of rapportage met actuele meetwaarden",
            "Notulen directiebeoordeling met evaluatie doelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "SMART kwaliteitsdoelstellingen vastgesteld per relevante functie, niveau of proces",
                "bewijslast": [
                    "Doelstellingenoverzicht met meetcriterium, frequentie en eigenaar",
                ],
            },
            {
                "id": "b",
                "eis": "Per doelstelling: actieplan met wie, wat, wanneer, middelen en evaluatiemethode",
                "bewijslast": [
                    "Actieplan of projectplan per KPI, bijv. klanttevredenheid >8, doorlooptijd <X dagen",
                ],
            },
            {
                "id": "c",
                "eis": "Voortgang bewaakt, gecommuniceerd en bijgesteld waar nodig",
                "bewijslast": [
                    "KPI-rapportage of dashboard met historische trend, besproken in directiebeoordeling",
                ],
            },
        ],
    },
    "6.3": {
        "normtekst": (
            "Wanneer de organisatie bepaalt dat wijzigingen in het "
            "kwaliteitsmanagementsysteem nodig zijn, moeten deze wijzigingen "
            "op een geplande manier worden doorgevoerd."
        ),
        "interpretatie": (
            "Veranderingen in het KMS (nieuwe processen, herziene procedures) "
            "mogen niet ad hoc worden doorgevoerd. Je moet nadenken over doel, "
            "integriteit van het systeem, beschikbare middelen en "
            "verantwoordelijkheden voordat je wijzigt."
        ),
        "bewijslast": [
            "Wijzigingsbeheerproces of change management procedure",
            "Logboek van KMS-wijzigingen met datum, reden en goedkeuring",
            "Bewijs van communicatie van wijzigingen aan betrokkenen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Doel en potentiële gevolgen van KMS-wijzigingen zijn overwogen vóór implementatie",
                "bewijslast": [
                    "Wijzigingsverzoek of change request met impactanalyse",
                ],
            },
            {
                "id": "b",
                "eis": "Integriteit van KMS geborgd: samenhang tussen processen bewaard na wijziging",
                "bewijslast": [
                    "Bewijs dat afhankelijke processen zijn beoordeeld bij wijziging",
                ],
            },
            {
                "id": "c",
                "eis": "Middelen beschikbaar voor de wijziging; verantwoordelijkheden belegd",
                "bewijslast": [
                    "Goedkeuringsrecord wijziging met eigenaar en resourcetoewijzing",
                ],
            },
        ],
    },
    "7.1": {
        "normtekst": (
            "De organisatie moet de benodigde middelen bepalen en beschikbaar "
            "stellen voor het opzetten, implementeren, onderhouden en continu "
            "verbeteren van het kwaliteitsmanagementsysteem."
        ),
        "interpretatie": (
            "Middelen omvatten mensen, infrastructuur, meetapparatuur en kennis. "
            "De directie moet actief besluiten hoeveel middelen het KMS krijgt. "
            "Te weinig middelen is een directe bedreiging voor de effectiviteit "
            "van het systeem."
        ),
        "bewijslast": [
            "Budget of resourceplan voor KMS-activiteiten",
            "Overzicht infrastructuur en onderhoudsprogramma",
            "Bewijs van beschikbaarheid gekwalificeerd personeel",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Mensen: benodigde capaciteit bepaald en beschikbaar (intern + extern)",
                "bewijslast": [
                    "Personeelsplanning, inhuurbeleid of capaciteitsoverzicht",
                ],
            },
            {
                "id": "b",
                "eis": "Infrastructuur: hardware, software, tooling bepaald, onderhouden en beschikbaar",
                "bewijslast": [
                    "Infrastructuuroverzicht (cloud, laptops, tooling) met onderhoudsbeleid",
                ],
            },
            {
                "id": "c",
                "eis": "Werkomgeving: beheersmaatregelen voor menselijke en fysieke factoren bepaald",
                "bewijslast": [
                    "Werkplekbeleid, thuis/kantoorrichtlijn of ergonomiebeleid",
                ],
            },
            {
                "id": "d",
                "eis": "Meet- en monitoringsmiddelen: passend en aantoonbaar geschikt (gekalibreerd waar nodig)",
                "bewijslast": [
                    "Overzicht meetsystemen (tijdregistratie, kwaliteitstools) met validatie",
                ],
            },
            {
                "id": "e",
                "eis": "Organisatiekennis bepaald, onderhouden en beschikbaar gesteld",
                "bewijslast": [
                    "Kennisbeheersysteem (Confluence, wiki, kennisdeling-sessies) met actueel bewijs",
                ],
            },
        ],
    },
    "7.2": {
        "normtekst": (
            "De organisatie moet de benodigde competentie bepalen van personen "
            "die het kwaliteitsmanagementsysteem beïnvloeden, en waarborgen "
            "dat deze competentie aanwezig is."
        ),
        "interpretatie": (
            "Competentie gaat verder dan een diploma: het is de aantoonbare "
            "bekwaamheid om een taak goed uit te voeren. Je moet weten welke "
            "competenties nodig zijn, wie ze heeft en wat je doet als er een "
            "gat zit."
        ),
        "bewijslast": [
            "Competentiematrix per functie of rol",
            "Opleidingsplan en trainingsrecords",
            "Diploma's, certificaten of beoordelingsverslagen als bewijs",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Benodigde competenties bepaald per functie/rol die KMS beïnvloedt",
                "bewijslast": [
                    "Competentiematrix of functieprofiel met vereiste kennis/vaardigheden",
                ],
            },
            {
                "id": "b",
                "eis": "Medewerkers zijn aantoonbaar competent op basis van opleiding, training of ervaring",
                "bewijslast": [
                    "Opleidingsrecords, certificaten of beoordelingsverslagen per medewerker",
                ],
            },
            {
                "id": "c",
                "eis": "Acties genomen waar competentiekloof bestaat (training, coaching, herindeling)",
                "bewijslast": [
                    "Opleidingsplan met geplande trainingen en status, of POP per medewerker",
                ],
            },
            {
                "id": "d",
                "eis": "Gedocumenteerde informatie bewaard als bewijs van competentie",
                "bewijslast": [
                    "HR-dossiers of personeelsdatabase met opleidingen/certificeringen",
                ],
            },
        ],
    },
    "7.3": {
        "normtekst": (
            "Personen die werkzaamheden verrichten onder aansturing van de "
            "organisatie moeten zich bewust zijn van het kwaliteitsbeleid, de "
            "relevante doelstellingen en hun bijdrage aan de effectiviteit van "
            "het KMS."
        ),
        "interpretatie": (
            "Bewustzijn verschilt van training: medewerkers moeten begrijpen "
            "waarom kwaliteit belangrijk is en wat hun eigen rol daarin is. "
            "Een auditor kan medewerkers interviewen om dit te toetsen."
        ),
        "bewijslast": [
            "Communicatieplan of bewustwordingsprogramma",
            "Aanwezigheidsregistraties van toolboxen of briefings",
            "Bewijs van medewerkersbegrip (quiz, evaluatie of interview)",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Medewerkers zijn aantoonbaar op de hoogte van het kwaliteitsbeleid",
                "bewijslast": [
                    "Bewijs van communicatie beleid: onboarding-document, intranet, teamsessie",
                ],
            },
            {
                "id": "b",
                "eis": "Medewerkers kennen de relevante kwaliteitsdoelstellingen van hun rol",
                "bewijslast": [
                    "Doelstellingen opgenomen in functieprofiel of teamsprint-doelen",
                ],
            },
            {
                "id": "c",
                "eis": "Medewerkers begrijpen hun bijdrage aan KMS-effectiviteit",
                "bewijslast": [
                    "Bewijs van bewustwordingssessie, toolbox of teambespreking",
                ],
            },
            {
                "id": "d",
                "eis": "Medewerkers begrijpen de gevolgen van non-conformiteit met KMS-eisen",
                "bewijslast": [
                    "Gedragsregels, kwaliteitsbeleid of onboarding met gevolgen niet-naleving",
                ],
            },
        ],
    },
    "7.4": {
        "normtekst": (
            "De organisatie moet de interne en externe communicatie bepalen die "
            "relevant is voor het kwaliteitsmanagementsysteem, inclusief wat, "
            "wanneer, met wie en hoe wordt gecommuniceerd."
        ),
        "interpretatie": (
            "Slechte communicatie is een veelvoorkomende oorzaak van "
            "kwaliteitsproblemen. Door communicatie expliciet te plannen "
            "voorkom je dat cruciale informatie niet aankomt of verouderd is. "
            "Dit geldt zowel intern als naar klanten en leveranciers."
        ),
        "bewijslast": [
            "Communicatiematrix of communicatieplan",
            "Voorbeelden van uitgevoerde communicatie (nieuwsbrieven, notulen)",
            "Procedure voor externe communicatie over KMS-onderwerpen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Bepaald: wat over het KMS gecommuniceerd wordt (intern en extern)",
                "bewijslast": [
                    "Communicatiematrix met onderwerp, doelgroep en frequentie",
                ],
            },
            {
                "id": "b",
                "eis": "Bepaald: wanneer, met wie en hoe gecommuniceerd wordt en wie verantwoordelijk is",
                "bewijslast": [
                    "Communicatieplan of overlegstructuur (sprint reviews, retro's, klantoverleg)",
                ],
            },
        ],
    },
    "7.5": {
        "normtekst": (
            "Het kwaliteitsmanagementsysteem van de organisatie moet gedocumenteerde "
            "informatie bevatten die door de norm vereist wordt en die de "
            "organisatie zelf noodzakelijk acht voor de effectiviteit van het KMS. "
            "Gedocumenteerde informatie moet worden beheerd."
        ),
        "interpretatie": (
            "Documentbeheer gaat over het waarborgen dat de juiste versie op de "
            "juiste plek beschikbaar is en dat verouderde documenten worden "
            "ingetrokken. Het gaat niet om het maken van zoveel mogelijk "
            "procedures, maar om de documenten die er echt toe doen."
        ),
        "bewijslast": [
            "Documentbeheer procedure of DMS-instelling",
            "Lijst met gedocumenteerde informatie (documentregister)",
            "Bewijs van versiebeheer en goedkeuringsproces",
            "Bewijs van beheer van extern gedocumenteerde informatie",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Alle vereiste gedocumenteerde informatie aanwezig (norm-eis + eigen keuzes)",
                "bewijslast": [
                    "Documentregister met verwijzingen naar alle KMS-documenten",
                ],
            },
            {
                "id": "b",
                "eis": "Documenten geïdentificeerd, beschreven, opgemaakt en goedgekeurd",
                "bewijslast": [
                    "DMS-instelling (Drive, Confluence) met versiebeheer en eigenaar per document",
                ],
            },
            {
                "id": "c",
                "eis": "Toegang, bescherming, distributie, opslag en vernietiging geregeld",
                "bewijslast": [
                    "Toegangsrechtenbeheer Drive of DMS, bewaarbeleid (retentie), vernietigingsprotocol",
                ],
            },
        ],
    },
    "8.1": {
        "normtekst": (
            "De organisatie moet de processen die nodig zijn voor de realisatie "
            "van producten en diensten plannen, implementeren, beheersen en "
            "monitoren door criteria vast te stellen en gedocumenteerde informatie "
            "bij te houden."
        ),
        "interpretatie": (
            "Operationele planning zorgt ervoor dat de uitvoering van werk "
            "gecontroleerd verloopt en aan de eisen voldoet. Je moet criteria "
            "bepalen voor acceptatie en bewijs bewaren dat processen zijn "
            "uitgevoerd zoals gepland."
        ),
        "bewijslast": [
            "Operationele procedures of werkinstructies",
            "Productie- of dienstverleningsplannen",
            "Gedocumenteerde informatie als bewijs van procesuitvoering",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Criteria voor processen en acceptatie vastgesteld en gedocumenteerd",
                "bewijslast": [
                    "Definition of Done, acceptatiecriteria of kwaliteitsplan per project",
                ],
            },
            {
                "id": "b",
                "eis": "Processen worden beheerst uitgevoerd; bewijs bewaard",
                "bewijslast": [
                    "Sprint-records, delivery checklists of projectverslagen als procesuitvoerings-bewijs",
                ],
            },
            {
                "id": "c",
                "eis": "Uitbestede processen beheerst (zie ook 8.4)",
                "bewijslast": [
                    "Overzicht uitbestede processen + beheersmaatregelen (SLA, evaluatie)",
                ],
            },
            {
                "id": "d",
                "eis": "Geplande wijzigingen beheerst; onvoorziene wijzigingen beoordeeld op gevolgen",
                "bewijslast": [
                    "Change log of sprint-review records met geregistreerde scope-wijzigingen",
                ],
            },
        ],
    },
    "8.2": {
        "normtekst": (
            "De organisatie moet communiceren met klanten over informatie over "
            "producten en diensten, behandeling van vragen en orders, feedback "
            "inclusief klachten, en noodgevallen. Klanteisen en wettelijke eisen "
            "moeten worden bepaald en beoordeeld."
        ),
        "interpretatie": (
            "Je kunt geen kwaliteit leveren als je niet precies weet wat de "
            "klant verwacht. Eisen moeten worden bepaald vóór acceptatie van "
            "een order. Dit clausule-cluster dwingt je tot systematische "
            "klantcommunicatie en eisenbeheer."
        ),
        "bewijslast": [
            "Offerteproces of contractbeoordelingsprocedure",
            "Contracten of orderbevestigingen met vastgelegde eisen",
            "Klantcommunicatierecords (e-mails, verslagen klantgesprekken)",
            "Klachtenregister en afhandelingsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Productinformatie beschikbaar en klantcommunicatie georganiseerd",
                "bewijslast": [
                    "Diensten/productoverzicht beschikbaar voor klanten (website, offertedoc)",
                ],
            },
            {
                "id": "b",
                "eis": "Klanteisen bepaald vóór acceptatie van opdracht (inclusief wettelijke eisen)",
                "bewijslast": [
                    "Contractbeoordelingsprocedure of offerte-checklijst met eisenvalidatie",
                ],
            },
            {
                "id": "c",
                "eis": "Klanteisen beoordeeld; afwijkingen opgelost vóór contractaccept",
                "bewijslast": [
                    "Getekend contract of opdrachtbevestiging als bewijs van eisafstemming",
                ],
            },
            {
                "id": "d",
                "eis": "Klachten en feedback ontvangen, vastgelegd en afgehandeld",
                "bewijslast": [
                    "Klachtenregister of klanttevredenheidssysteem met afhandelingsrecords",
                ],
            },
        ],
    },
    "8.3": {
        "normtekst": (
            "De organisatie moet een proces opzetten, implementeren en onderhouden "
            "voor het ontwerpen en ontwikkelen van producten en diensten, inclusief "
            "planning, inputs, beheersmaatregelen, outputs en wijzigingsbeheer."
        ),
        "interpretatie": (
            "Ontwerpbeheersing voorkomt dat producten of diensten de markt "
            "bereiken zonder validatie. Het gaat erom dat ontwerpeisen helder "
            "zijn, dat verificatie plaatsvindt en dat wijzigingen worden "
            "beoordeeld op impact. Mag worden uitgesloten als er geen O&O is."
        ),
        "bewijslast": [
            "Ontwerp- en ontwikkelingsprocedure",
            "Ontwerp inputs en outputs per project (specificaties, tekeningen)",
            "Verificatie- en validatierapporten",
            "Overzicht ontwerpwijzigingen met goedkeuringsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Ontwerp- en ontwikkelingsproces bepaald en gedocumenteerd (planning, reviews, verificatie, validatie)",
                "bewijslast": [
                    "SDLC-beschrijving, sprint-cadans of productdevelopment-procedure",
                ],
            },
            {
                "id": "b",
                "eis": "Ontwerp-inputs bepaald: functionele eisen, wet/regelgeving, eerdere ervaringen",
                "bewijslast": [
                    "User stories, backlog of functionele specificaties per project als inputs",
                ],
            },
            {
                "id": "c",
                "eis": "Beheersmaatregelen: design reviews, verificatie en validatie uitgevoerd",
                "bewijslast": [
                    "Code review records, test-rapporten, acceptatietest met klant",
                ],
            },
            {
                "id": "d",
                "eis": "Ontwerp-outputs voldoen aan inputs; gedocumenteerd",
                "bewijslast": [
                    "Release notes of Definition of Done-check als bewijs outputs vs inputs",
                ],
            },
            {
                "id": "e",
                "eis": "Ontwerp-wijzigingen geïdentificeerd, beoordeeld, goedgekeurd en gedocumenteerd",
                "bewijslast": [
                    "Change log of bijgehouden sprint-backlog-wijzigingen met goedkeuring",
                ],
            },
        ],
    },
    "8.4": {
        "normtekst": (
            "De organisatie moet waarborgen dat extern geleverde processen, "
            "producten en diensten voldoen aan de gestelde eisen. Zij moet "
            "criteria bepalen voor beoordeling, selectie en monitoring van "
            "externe leveranciers."
        ),
        "interpretatie": (
            "Uitbesteding verschuift uitvoering maar niet verantwoordelijkheid. "
            "Je blijft verantwoordelijk voor wat een leverancier levert. "
            "Leveranciersbeheer moet risicogebaseerd zijn: kritieke leveranciers "
            "verdienen meer aandacht dan eenmalige toeleveranciers."
        ),
        "bewijslast": [
            "Leverancierslijst met kwalificatiestatus",
            "Leveranciersbeoordeling procedure en evaluatierecords",
            "Inkooporders of contracten met kwaliteitseisen",
            "Inspectierapportages of acceptatierecords van inkomende goederen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Selectie- en evaluatiecriteria voor externe leveranciers bepaald (risicogebaseerd)",
                "bewijslast": [
                    "Leverancierslijst met kwalificatiestatus en risicoklasse (bijv. SIM/Procura als kritiek)",
                ],
            },
            {
                "id": "b",
                "eis": "Beheersmaatregel proportioneel aan impact extern geleverde output op eindproduct",
                "bewijslast": [
                    "Bewijs van monitoring kritieke leveranciers (SLA-review, audit, beoordeling)",
                ],
            },
            {
                "id": "c",
                "eis": "Inkoopvereisten gecommuniceerd naar leveranciers (kwaliteitseisen, specificaties)",
                "bewijslast": [
                    "Contracten of inkooporders met expliciete kwaliteits- of service-eisen",
                ],
            },
        ],
    },
    "8.5": {
        "normtekst": (
            "De organisatie moet de productie en dienstverlening uitvoeren onder "
            "beheerste omstandigheden, inclusief beschikbaarheid van informatie, "
            "geschikte infrastructuur, monitoring, en maatregelen voor "
            "identificatie en traceerbaarheid."
        ),
        "interpretatie": (
            "Beheerste omstandigheden betekenen dat je weet wat je maakt, "
            "hoe je het maakt en dat je het kunt terugvinden als er iets "
            "misgaat. Traceerbaarheid is essentieel voor effectief "
            "probleemoplossen en terugroepacties."
        ),
        "bewijslast": [
            "Werkinstructies voor kernprocessen",
            "Productie- of servicerecords met identificatiegegevens",
            "Traceerbaarheidssysteem (batch, serienummer of equivalent)",
            "Registraties van vrijgave en afleveringsactiviteiten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Beheerste omstandigheden: werkinstructies, goedgekeurde middelen, monitoring tijdens uitvoering",
                "bewijslast": [
                    "Werkinstructies of runbooks voor kernprocessen (deployments, klantdelivery)",
                ],
            },
            {
                "id": "b",
                "eis": "Identificatie en traceerbaarheid van outputs gedurende de uitvoering",
                "bewijslast": [
                    "Versienummering, sprint-labels of projectidentificatie in leverables",
                ],
            },
            {
                "id": "c",
                "eis": "Eigendom van klanten en externe partijen geïdentificeerd, beschermd en gerapporteerd",
                "bewijslast": [
                    "Data-verwerkersovereenkomst of klantdatabeheerbeleid (AVG)",
                ],
            },
            {
                "id": "d",
                "eis": "Bewaring en preservering van producten/diensten geregeld",
                "bewijslast": [
                    "Back-upbeleid, archivering of bewaarprotocol voor klantdata en leverables",
                ],
            },
            {
                "id": "e",
                "eis": "Activiteiten na levering bepaald (garantie, service, support, onderhoud)",
                "bewijslast": [
                    "Serviceovereenkomst, garantiebepaling of supportprocedure na oplevering",
                ],
            },
        ],
    },
    "8.6": {
        "normtekst": (
            "De organisatie moet op geplande momenten verificaties uitvoeren om "
            "te waarborgen dat aan de eisen voor producten en diensten is voldaan. "
            "Producten en diensten mogen pas worden vrijgegeven als aan alle "
            "gestelde eisen is voldaan."
        ),
        "interpretatie": (
            "Vrijgavebeheersing zorgt ervoor dat niets de klant bereikt zonder "
            "formele goedkeuring. De vrijgave moet worden gedocumenteerd inclusief "
            "wie heeft vrijgegeven. Dit is een direct controlemoment voor de "
            "auditor."
        ),
        "bewijslast": [
            "Inspectie- of testprocedure voor producten/diensten",
            "Keurings- of testrecords met handtekening vrijgavebevoegde",
            "Vrijgaveformulieren of digitale goedkeuringsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Verificaties op geplande momenten uitgevoerd om conformiteit te borgen",
                "bewijslast": [
                    "Test- of reviewrecords per sprint of oplevering (automated tests, peer review)",
                ],
            },
            {
                "id": "b",
                "eis": "Producten/diensten pas vrijgegeven als aan alle eisen is voldaan; wie/wanneer gedocumenteerd",
                "bewijslast": [
                    "Acceptatieformulier of digitale goedkeuring klant of productowner met datum en naam",
                ],
            },
        ],
    },
    "8.7": {
        "normtekst": (
            "De organisatie moet producten en diensten die niet voldoen aan de "
            "eisen identificeren en beheersen om onbedoeld gebruik of levering te "
            "voorkomen. Afwijkingen moeten worden gedocumenteerd."
        ),
        "interpretatie": (
            "Niet-conformiteiten moeten worden gevonden vóórdat ze de klant "
            "bereiken. Goede non-conformiteitsbeheer geeft ook waardevolle "
            "data voor verbeterinitiatieven. De auditor controleert of "
            "afwijkingen consequent worden vastgelegd en afgehandeld."
        ),
        "bewijslast": [
            "Non-conformiteitenprocedure",
            "Non-conformiteitenregister of NCR-formulieren",
            "Bewijs van correctieve maatregelen bij herhaalde afwijkingen",
            "Klantcommunicatie bij afwijkend geleverd product",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Non-conforme outputs geïdentificeerd en onder controle gebracht (gebruik/levering voorkomen)",
                "bewijslast": [
                    "Non-conformiteitenregister of bug tracker met status (geblokkeerd/terug naar dev)",
                ],
            },
            {
                "id": "b",
                "eis": "Actie genomen: correctie, retentie, retour of uitzonderingsgodkeuring",
                "bewijslast": [
                    "NCR of incident record met beschrijving actie en uitkomst",
                ],
            },
            {
                "id": "c",
                "eis": "Klant of bevoegde autoriteit geïnformeerd indien non-conform product/dienst geleverd",
                "bewijslast": [
                    "Communicatierecord bij afwijkende levering (e-mail, ticket, notitie klantoverleg)",
                ],
            },
            {
                "id": "d",
                "eis": "Gedocumenteerde informatie als bewijs: beschrijving afwijking, acties en eventuele uitzonderingstoestemming",
                "bewijslast": [
                    "Compleet NCR-formulier of gestructureerd incident-ticket met alle vereiste velden",
                ],
            },
        ],
    },
    "9.1": {
        "normtekst": (
            "De organisatie moet bepalen wat, hoe en wanneer wordt gemonitord, "
            "gemeten, geanalyseerd en beoordeeld. Zij moet de prestaties en de "
            "effectiviteit van het kwaliteitsmanagementsysteem evalueren."
        ),
        "interpretatie": (
            "Meten zonder analyseren is zinloos. Je moet bewuste keuzes maken "
            "over welke indicatoren iets zeggen over proceskwaliteit en "
            "klanttevredenheid. Klanttevredenheid meten is expliciet vereist, "
            "de methode mag je zelf kiezen."
        ),
        "bewijslast": [
            "KPI-overzicht met meetmethode en frequentie",
            "Klanttevredenheidsmetingen (enquête, NPS, klachtentrend)",
            "Analyse- en beoordelingsrapportages",
            "Bewijs van opvolging van analyseresultaten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Bepaald: wat, hoe en wanneer gemonitord/gemeten wordt (processen, producten, KMS)",
                "bewijslast": [
                    "KPI-overzicht of monitoringsplan met meetmethode, frequentie en eigenaar",
                ],
            },
            {
                "id": "b",
                "eis": "Klanttevredenheid gemeten (methode naar eigen keuze: NPS, enquête, klachtentrend)",
                "bewijslast": [
                    "Klanttevredenheidsresultaten, NPS-score of klachtenanalyse met datum",
                ],
            },
            {
                "id": "c",
                "eis": "Data geanalyseerd en geëvalueerd; resultaten input voor directiebeoordeling",
                "bewijslast": [
                    "Analyse-rapportage of KPI-dashboard als input directiebeoordeling",
                ],
            },
            {
                "id": "d",
                "eis": "Analyseresultaten leiden tot opvolging en aantoonbare verbeteracties",
                "bewijslast": [
                    "Verbeteracties of besluitenlijst gekoppeld aan monitoringuitkomsten",
                ],
            },
        ],
    },
    "9.2": {
        "normtekst": (
            "De organisatie moet op geplande tijdstippen interne audits uitvoeren "
            "om vast te stellen of het kwaliteitsmanagementsysteem voldoet aan "
            "de eisen en effectief is geïmplementeerd en onderhouden."
        ),
        "interpretatie": (
            "Interne audits zijn de zelfreflectie van het KMS. Ze zijn geen "
            "formaliteit maar een echt toetsinstrument. Een auditprogramma moet "
            "alle processen en clausules periodiek omvatten en resultaten moeten "
            "leiden tot opvolging."
        ),
        "bewijslast": [
            "Jaarlijks intern auditprogramma",
            "Auditplannen en auditverslagen",
            "Non-conformiteiten en verbeteracties voortkomend uit interne audits",
            "Bewijs van kwalificatie van interne auditoren",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Auditprogramma vastgesteld: frequentie, methoden, verantwoordelijkheden, rapportage",
                "bewijslast": [
                    "Jaarlijks auditprogramma met alle KMS-clausules en processen gedekt",
                ],
            },
            {
                "id": "b",
                "eis": "Auditors zijn competent en objectief (niet eigen werk auditen)",
                "bewijslast": [
                    "Kwalificatierecord interne auditor of gebruik externe auditor voor zelfevaluatie",
                ],
            },
            {
                "id": "c",
                "eis": "Auditbevindingen gerapporteerd aan verantwoordelijk management",
                "bewijslast": [
                    "Auditverslag of auditrapport gericht aan directie/proceseigenaar",
                ],
            },
            {
                "id": "d",
                "eis": "Correcties en verbeteracties tijdig doorgevoerd na bevindingen",
                "bewijslast": [
                    "Actieoverzicht uit interne audits met status en afdoening",
                ],
            },
        ],
    },
    "9.3": {
        "normtekst": (
            "Het topmanagement moet het kwaliteitsmanagementsysteem op geplande "
            "tijdstippen beoordelen om te waarborgen dat het passend, adequaat "
            "en effectief blijft. De beoordeling moet specifieke inputs bevatten "
            "en outputs produceren."
        ),
        "interpretatie": (
            "De directiebeoordeling is het moment waarop de directie formeel "
            "verantwoordelijkheid neemt voor het KMS. Het is geen standaard "
            "vergadering: er zijn verplichte agenda-items en de uitkomsten "
            "moeten leiden tot concrete besluiten over middelen en verbetering."
        ),
        "bewijslast": [
            "Notulen directiebeoordeling (met alle verplichte inputs)",
            "Besluitenlijst met acties, eigenaren en termijnen",
            "Bewijs van opvolging van acties uit vorige directiebeoordeling",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Inputs aanwezig: status vorige review, veranderingen, prestaties, resources, risico's, verbetermogelijkheden",
                "bewijslast": [
                    "Directiebeoordeling-agenda met alle verplichte ISO 9001 §9.3.2 input-items",
                ],
            },
            {
                "id": "b",
                "eis": "Outputs zijn besluiten: verbeteringen, resource-behoeften, KMS-wijzigingen",
                "bewijslast": [
                    "Besluitenlijst uit directiebeoordeling met eigenaar en deadline per actie",
                ],
            },
            {
                "id": "c",
                "eis": "Acties uit vorige directiebeoordeling zijn opgevolgd en afgerond",
                "bewijslast": [
                    "Status-overzicht acties vorige review: open/gesloten/verschoven met motivatie",
                ],
            },
        ],
    },
    "10.1": {
        "normtekst": (
            "De organisatie moet kansen voor verbetering bepalen en selecteren "
            "en de nodige acties implementeren om aan klanteisen te voldoen en "
            "de klanttevredenheid te verhogen."
        ),
        "interpretatie": (
            "Verbetering is geen toevallige activiteit maar een systematische "
            "verplichting. De norm vraagt om bewuste keuzes over waar je "
            "investeert in verbetering, onderbouwd door data uit monitoring en "
            "analyse."
        ),
        "bewijslast": [
            "Verbeterregister of verbeterplannen",
            "Koppeling van verbeteracties aan data (klachten, audits, KPI's)",
            "Bewijs van implementatie en effectiviteitstoetsing van verbeteringen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Verbetermogelijkheden bepaald op basis van data (klachten, KPI's, audits)",
                "bewijslast": [
                    "Verbeterregister of backlog met bron (klacht, audit, klanttevredenheid)",
                ],
            },
            {
                "id": "b",
                "eis": "Verbeteracties geïmplementeerd om aan klanteisen te voldoen en tevredenheid te verhogen",
                "bewijslast": [
                    "Bewijs van uitgevoerde verbeteringen en gemeten effect op klantervaring",
                ],
            },
        ],
    },
    "10.2": {
        "normtekst": (
            "Bij het optreden van een non-conformiteit moet de organisatie "
            "reageren, de oorzaak bepalen, beoordelen of vergelijkbare situaties "
            "bestaan en correctieve maatregelen nemen. Effectiviteit moet worden "
            "beoordeeld en gedocumenteerde informatie bewaard."
        ),
        "interpretatie": (
            "Correctieve maatregelen gaan over het wegnemen van oorzaken, niet "
            "alleen het oplossen van het symptoom. Een goede oorzaakanalyse "
            "(5x waarom, visgraatdiagram) is het bewijs dat je serieus omgaat "
            "met non-conformiteiten."
        ),
        "bewijslast": [
            "Correctieve-maatregelenprocedure",
            "NCR's met oorzaakanalyse en corrigerende maatregel",
            "Bewijs van effectiviteitscontrole na implementatie maatregel",
            "Geactualiseerd risicoregister op basis van non-conformiteiten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Reactie op non-conformiteit: corrigeer het probleem en pak de gevolgen aan",
                "bewijslast": [
                    "NCR of incident-ticket met beschrijving actie en afdoening",
                ],
            },
            {
                "id": "b",
                "eis": "Oorzaakanalyse uitgevoerd om herhaling te voorkomen",
                "bewijslast": [
                    "Oorzaakanalyse (5×waarom, visgraat) opgenomen in NCR",
                ],
            },
            {
                "id": "c",
                "eis": "Beoordeling of vergelijkbare non-conformiteiten elders bestaan of kunnen ontstaan",
                "bewijslast": [
                    "Bewijs van scope-check: zijn vergelijkbare processen/projecten beoordeeld?",
                ],
            },
            {
                "id": "d",
                "eis": "Maatregel geïmplementeerd en effectiviteit beoordeeld; KMS bijgewerkt waar nodig",
                "bewijslast": [
                    "Effectiviteitscontrole in NCR of audit-bevinding met bewijs van afdoening",
                ],
            },
        ],
    },
    "10.3": {
        "normtekst": (
            "De organisatie moet de geschiktheid, adequaatheid en effectiviteit "
            "van het kwaliteitsmanagementsysteem continu verbeteren. Zij moet "
            "resultaten van analyse en beoordeling gebruiken om verbetermogelijkheden "
            "te bepalen."
        ),
        "interpretatie": (
            "Continue verbetering (kaizen-gedachte) is de overkoepelende "
            "ambitie van ISO 9001. Het gaat niet alleen om het herstellen van "
            "fouten, maar om het proactief verbeteren van prestaties. De "
            "PDCA-cyclus is hiervoor het raamwerk."
        ),
        "bewijslast": [
            "Aantoonbare trend in KPI-verbetering over meerdere periodes",
            "Verbeterinitiatieven voortkomend uit directiebeoordeling",
            "Bewijs van PDCA-cyclus toepassing in minimaal één verbeterproject",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Geschiktheid, adequaatheid en effectiviteit KMS worden actief verbeterd",
                "bewijslast": [
                    "Verbeterregister of verbeterindicatoren met aantoonbare trend over tijd",
                ],
            },
            {
                "id": "b",
                "eis": "Uitkomsten van analyse, directiebeoordeling en audits worden gebruikt als verbeterinput",
                "bewijslast": [
                    "Koppeling: directiebeoordeling-output → verbeteractie in verbeterregister",
                ],
            },
            {
                "id": "c",
                "eis": "Continue verbetering is aantoonbaar (niet incidenteel, maar structureel geborgd)",
                "bewijslast": [
                    "Bewijs van PDCA-cyclus in minimaal één verbeterproject (plan, do, check, act)",
                ],
            },
        ],
    },
}
