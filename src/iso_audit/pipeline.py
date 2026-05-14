"""Orchestrator: ISO audit pipeline.

Gemigreerd uit `Ops_to_Biz/audit/pipeline.py` per milestone B §2.5.10.
Wijzigingen: imports vernieuwd naar `iso_audit.*`; type-hints aangevuld
voor mypy --strict; CLI ondersteunt optionele `argv` voor tests;
`subprocess` voor `gws auth status` gebruikt bandit-nosec markers.

Gebruik:
    python -m iso_audit.pipeline --norm 9001
    python -m iso_audit.pipeline --norm 27001
    python -m iso_audit.pipeline --norm beide

    # Eén hoofdstuk uitvoeren (minder API-calls, sneller):
    python -m iso_audit.pipeline --norm 9001 --chapter 4
    python -m iso_audit.pipeline --norm beide --chapter 8

    # Dry-run zonder externe verbindingen (test + lokale output):
    python -m iso_audit.pipeline --local-only --norm 9001

    # Alleen template aanmaken (eerste keer):
    python -m iso_audit.pipeline --setup-template

Omgevingsvariabelen: zie .env.example.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess  # nosec B404 — gws CLI is een gecontroleerde shell-laag
import sys
from datetime import date, timedelta
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _valideer_env() -> None:
    """Controleer dat gws beschikbaar en ingelogd is."""
    if not shutil.which("gws"):
        logger.error("gws CLI niet gevonden in PATH.")
        sys.exit(1)
    try:
        result = subprocess.run(  # nosec B603 — args zijn statisch
            ["gws", "auth", "status"],  # nosec B607
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        status = json.loads(result.stdout) if result.stdout.strip() else {}
        if not status.get("token_valid", False):
            logger.warning(
                "gws auth token niet geldig (%s). Voer `gws auth login` uit als API-calls falen.",
                status.get("token_error", "onbekend"),
            )
    except Exception:
        pass


_LOKALE_TEST_BEVINDINGEN: list[dict[str, Any]] = [
    {
        "clausule": "4.1",
        "clausule_titel": "Inzicht in de organisatie en haar context",
        "document_naam": "[TESTDATA] Contextanalyse_2025.docx",
        "herkomst": "Drive",
        "classificatie": "positief",
        "beschrijving": (
            "De organisatie heeft een gedocumenteerde contextanalyse "
            "uitgevoerd. Interne en externe factoren zijn beschreven."
        ),
        "onderbouwing": ("ISO 9001:2015 §4.1 vereist begrip van interne en externe context."),
        "pre_classificatie": None,
    },
    {
        "clausule": "5.2",
        "clausule_titel": "Beleid",
        "document_naam": "[TESTDATA] Kwaliteitsbeleid_v2.docx",
        "herkomst": "Drive",
        "classificatie": "OFI",
        "beschrijving": (
            "Het kwaliteitsbeleid is aanwezig maar wordt niet actief "
            "gecommuniceerd naar alle medewerkers."
        ),
        "onderbouwing": (
            "ISO 9001:2015 §5.2.2 vereist dat het beleid beschikbaar is "
            "als gedocumenteerde informatie."
        ),
        "pre_classificatie": None,
    },
    {
        "clausule": "8.1",
        "clausule_titel": "Operationele planning en beheersing",
        "document_naam": "[TESTDATA] Miro sticky: geen gedocumenteerd proces",
        "herkomst": "Miro",
        "classificatie": "NC",
        "beschrijving": (
            "Er is geen gedocumenteerde operationele planning voor het "
            "primaire proces aangetroffen."
        ),
        "onderbouwing": (
            "ISO 9001:2015 §8.1 vereist planning, implementatie en "
            "beheersing van operationele processen."
        ),
        "pre_classificatie": "rood",
    },
]

_LOKALE_TEST_ONTBREKEND: list[dict[str, Any]] = [
    {
        "clausule": "9.3",
        "titel": "Directiebeoordeling",
        "reden": "[TESTDATA] Geen bewijs van directiebeoordeling gevonden",
    },
]


def run_local_only(norm: str) -> str:
    """Dry-run: synthetische data → lokale Markdown + CSV + Excel."""
    from iso_audit.classification.thema import bepaal_thema
    from iso_audit.reporting.local_report import schrijf_rapport
    from iso_audit.reporting.tabular_report import schrijf_csv, schrijf_excel

    logger.info("=== ISO Audit Pipeline — LOCAL ONLY (testdata) ===")
    logger.info("Norm: %s | Geen Drive/Claude/Sheets-verbinding", norm)

    management_summary = (
        "**[TESTDATA]** Dit rapport is gegenereerd met synthetische "
        "testbevindingen zonder verbinding met Google Drive of de "
        "Claude API. Gebruik `--local-only` uitsluitend voor het testen "
        "van de rapportage-logica."
    )

    for bev in _LOKALE_TEST_BEVINDINGEN:
        bev.setdefault("thema", bepaal_thema(bev))

    lokaal_pad = schrijf_rapport(
        _LOKALE_TEST_BEVINDINGEN,
        _LOKALE_TEST_ONTBREKEND,
        [],
        management_summary,
        norm,
    )
    logger.info("Lokaal testrapport: %s", lokaal_pad)

    csv_pad = schrijf_csv(_LOKALE_TEST_BEVINDINGEN, norm)
    xlsx_pad = schrijf_excel(_LOKALE_TEST_BEVINDINGEN, norm)
    logger.info("Tabulair: %s  |  %s", csv_pad, xlsx_pad)

    return lokaal_pad


_RUIS_PATTERNS: tuple[str, ...] = (
    "VERWIJDEREN",
    "TEMPLATE KOPIE MAKEN",
)
_RUIS_PREFIXES: tuple[str, ...] = (
    "OUD:",
    "OUD ",
    "Oud:",
)


def _is_ruis(document_naam: str) -> bool:
    """Drive-rommel detector: documenten die niet in een auditrapport horen."""
    if not document_naam:
        return False
    naam = document_naam.strip()
    if any(p in naam for p in _RUIS_PATTERNS):
        return True
    return naam.startswith(_RUIS_PREFIXES)


def _filter_ruis(bevindingen: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Verwijder ruis-bevindingen; retourneer (schoon, aantal_geskipped)."""
    schoon = [b for b in bevindingen if not _is_ruis(b.get("document_naam", ""))]
    geskipped = len(bevindingen) - len(schoon)
    if geskipped:
        logger.info(
            "Ruis-filter: %d bevinding(en) uit Drive-archief weggelaten "
            "(VERWIJDEREN/TEMPLATE KOPIE MAKEN/OUD-prefix)",
            geskipped,
        )
    return schoon, geskipped


def run_setup_template() -> None:
    """Eénmalige setup: template aanmaken in Drive."""
    from iso_audit.reporting.template_setup import create_template, verify_placeholders

    folder_id = os.environ.get("AUDIT_DRIVE_FOLDER_ID", "")
    logger.info("Template aanmaken...")
    doc_id = create_template(folder_id)
    ontbrekend = verify_placeholders(doc_id)
    if ontbrekend:
        logger.warning("Voeg AUDIT_TEMPLATE_DOC_ID=%s toe aan .env", doc_id)
    else:
        logger.info("Template klaar. Voeg toe aan .env: AUDIT_TEMPLATE_DOC_ID=%s", doc_id)


def run_audit(
    norm: str,
    no_review: bool = False,
    write_sheets: bool = False,
    chapter: str | None = None,
    scherpte: float = 1.0,
    thema_llm: bool = False,
    rehash: bool = False,
    dry_run_cost: bool = False,
) -> None:
    """Volledige auditpipeline uitvoeren."""
    from iso_audit.classification.clause_mapping import (
        filter_clause_map,
        koppel_documenten,
        laad_clause_map,
        ontbrekende_dekking,
    )
    from iso_audit.classification.findings import (
        classificeer_alle_bevindingen,
        review_en_bevestig,
        schat_kosten,
    )
    from iso_audit.classification.thema import bepaal_thema
    from iso_audit.miro.ingest import (
        haal_notities_op,
        koppel_aan_clausules,
        merge_met_drive_bevindingen,
    )
    from iso_audit.notification import (
        stuur_calendar_uitnodiging,
        stuur_gmail_notificatie,
    )
    from iso_audit.reporting.local_report import schrijf_rapport
    from iso_audit.reporting.report_generation import (
        _genereer_management_summary,
        genereer_rapport,
    )
    from iso_audit.reporting.sheets_gws import sla_op_in_sheets
    from iso_audit.reporting.slide_summary import genereer_slides
    from iso_audit.reporting.tabular_report import schrijf_csv, schrijf_excel
    from iso_audit.sources.drive import haal_documenten_op

    logger.info(
        "=== ISO Audit Pipeline gestart (norm: %s, rehash: %s, dry-run-cost: %s) ===",
        norm,
        rehash,
        dry_run_cost,
    )

    logger.info("Stap 1/7: Clausule-map laden...")
    clause_map = laad_clause_map(norm)
    if chapter:
        clause_map = filter_clause_map(clause_map, chapter)
        logger.info("Hoofdstuk-filter actief: alleen clausule %s.*", chapter)

    logger.info("Stap 2/7: Drive-documenten inlezen...")
    documenten, handmatige_review = haal_documenten_op()
    if handmatige_review:
        logger.warning(
            "%d bestand(en) vereisen handmatige review: %s",
            len(handmatige_review),
            [h["naam"] for h in handmatige_review],
        )

    logger.info("Stap 3/7: Miro-notities inlezen...")
    miro_notities: list[dict[str, Any]] = []
    try:
        miro_notities_raw = haal_notities_op()
        miro_notities = koppel_aan_clausules(miro_notities_raw, clause_map)
        logger.info("%d Miro-notities ingelezen", len(miro_notities))
    except OSError as e:
        logger.warning("Miro overgeslagen: %s", e)
    except Exception as e:
        logger.warning("Miro-ingest mislukt (niet kritiek): %s", e)

    logger.info("Stap 4/7: Documenten koppelen aan clausules...")
    cutoff = (date.today() - timedelta(days=2 * 365)).isoformat()
    gekoppeld_alle, niet_geclassificeerd = koppel_documenten(documenten, clause_map)
    gearchiveerd = [d for d in gekoppeld_alle if (d.get("modified_at") or "") < cutoff]
    gekoppeld = [d for d in gekoppeld_alle if (d.get("modified_at") or "") >= cutoff]
    logger.info(
        "Leeftijdsfilter (%s): %d actief, %d gearchiveerd (>2 jaar oud)",
        cutoff,
        len(gekoppeld),
        len(gearchiveerd),
    )

    _alle_input = merge_met_drive_bevindingen(
        miro_notities, [{**doc, "herkomst": "Drive"} for doc in gekoppeld]
    )
    ontbrekend = ontbrekende_dekking(gekoppeld, miro_notities, clause_map)

    if niet_geclassificeerd:
        logger.warning(
            "%d document(en) zonder clausule-match: %s",
            len(niet_geclassificeerd),
            [d["naam"] for d in niet_geclassificeerd],
        )

    if dry_run_cost:
        logger.info("Stap 5/7: Kostenschatting (dry-run, GEEN API-calls)...")
        schatting = schat_kosten(
            gekoppeld,
            miro_notities,
            clause_map,
            norm=norm,
            scherpte=scherpte,
            rehash=rehash,
        )
        logger.info("=== Kostenschatting ===")
        for k, v in schatting.items():
            logger.info("  %-25s %s", k + ":", v)
        logger.info("=== Einde dry-run-cost (stoppen voor API-calls) ===")
        return

    logger.info(
        "Stap 5/7: Bevindingen classificeren via Claude... (scherpte=%.1f, rehash=%s)",
        scherpte,
        rehash,
    )
    bevindingen = classificeer_alle_bevindingen(
        gekoppeld,
        miro_notities,
        clause_map,
        norm=norm,
        scherpte=scherpte,
        rehash=rehash,
    )

    logger.info("Stap 6/7: Menselijke review...")
    bevestigde_bevindingen = review_en_bevestig(bevindingen, auto_accept=no_review)
    bevestigde_bevindingen, _ = _filter_ruis(bevestigde_bevindingen)

    if write_sheets or os.environ.get("AUDIT_SHEETS_ID"):
        sheets_id = sla_op_in_sheets(bevestigde_bevindingen, ontbrekend)
        logger.info("Bevindingen opgeslagen in Sheets: %s", sheets_id)
    else:
        logger.info("Sheets-schrijven overgeslagen (geen AUDIT_SHEETS_ID of --write-sheets).")

    logger.info("Stap 7/7: Rapport en presentatie genereren...")
    try:
        management_summary = _genereer_management_summary(bevestigde_bevindingen)
    except Exception as e:
        logger.warning("Management summary genereren mislukt (%s) — placeholder gebruikt.", e)
        nc = sum(1 for b in bevestigde_bevindingen if b["classificatie"] == "NC")
        ofi = sum(1 for b in bevestigde_bevindingen if b["classificatie"] == "OFI")
        management_summary = (
            f"_(Automatische samenvatting niet beschikbaar: {e})_\n\n"
            f"Bevindingen: {len(bevestigde_bevindingen)} totaal — "
            f"{nc} NC, {ofi} OFI."
        )

    llm_themas: dict[str, str] = {}
    if thema_llm:
        try:
            from iso_audit.classification.thema import verfijn_overig

            llm_themas = verfijn_overig(bevestigde_bevindingen)
        except Exception as e:
            logger.warning("LLM thema-verfijning mislukt (niet kritiek): %s", e)

    for i, bev in enumerate(bevestigde_bevindingen):
        bev_id = str(bev.get("id") or bev.get("_bev_id") or i)
        bev["_bev_id"] = bev_id
        bev["thema"] = llm_themas.get(bev_id) or bepaal_thema(bev)

    lokaal_pad = schrijf_rapport(
        bevestigde_bevindingen,
        ontbrekend,
        handmatige_review,
        management_summary,
        norm,
        gearchiveerd=gearchiveerd,
        scherpte=scherpte,
    )
    logger.info("Lokaal rapport (md): %s", lokaal_pad)

    _converteer_md_naar_html_docx_pdf(lokaal_pad)

    try:
        csv_pad = schrijf_csv(
            bevestigde_bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas
        )
        xlsx_pad = schrijf_excel(
            bevestigde_bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas
        )
        logger.info("Tabulair: %s  |  %s", csv_pad, xlsx_pad)
    except Exception as e:
        logger.warning("Tabulaire export mislukt (niet kritiek): %s", e)

    rapport_doc_id: str | None = None
    slides_id: str | None = None
    if os.environ.get("AUDIT_TEMPLATE_DOC_ID"):
        rapport_doc_id = genereer_rapport(
            bevestigde_bevindingen, ontbrekend, handmatige_review, norm
        )
        slides_id = genereer_slides(bevestigde_bevindingen, norm)
        logger.info("Rapport:     https://docs.google.com/document/d/%s", rapport_doc_id)
        logger.info("Presentatie: https://docs.google.com/presentation/d/%s", slides_id)
    else:
        logger.info("AUDIT_TEMPLATE_DOC_ID niet ingesteld — Google Docs/Slides overgeslagen.")

    if rapport_doc_id and slides_id:
        stuur_calendar_uitnodiging(rapport_doc_id, slides_id, norm)
        stuur_gmail_notificatie(rapport_doc_id, slides_id, norm, bevestigde_bevindingen)

    logger.info("=== Audit pipeline klaar ===")


def _converteer_md_naar_html_docx_pdf(md_pad: str) -> None:
    """Keten md → html → docx + pdf; elke stap is best-effort."""
    try:
        from iso_audit.reporting.md_to_html import converteer as md_to_html

        html_pad = md_to_html(md_pad)
        logger.info("HTML: %s", html_pad)
    except Exception as e:
        logger.warning("HTML-conversie mislukt: %s", e)
        return

    try:
        from iso_audit.reporting.html_to_docx import converteer as html_to_docx

        logger.info("DOCX: %s", html_to_docx(html_pad))
    except Exception as e:
        logger.warning("DOCX-conversie mislukt: %s", e)
    try:
        from iso_audit.reporting.html_to_pdf import converteer as html_to_pdf

        logger.info("PDF: %s", html_to_pdf(html_pad))
    except Exception as e:
        logger.warning("PDF-conversie mislukt: %s", e)


def run_report_only(norm: str, scherpte: float = 1.0, thema_llm: bool = False) -> None:
    """Regenereer rapport vanuit bestaande bevindingen-DB. Geen Drive/Miro/classificatie.

    Doel: iteratie op rapport-taal (management summary, OFI-kop, aanbevelingen)
    zonder kosten op de classificatielaag. Gebruikt de bevindingen die al in
    `output/audit_*.db` staan van een eerdere run.
    """
    from iso_audit.classification.clause_mapping import laad_clause_map
    from iso_audit.classification.thema import bepaal_thema
    from iso_audit.reporting.local_report import schrijf_rapport
    from iso_audit.reporting.report_generation import _genereer_management_summary
    from iso_audit.reporting.sheets_gws import sla_op_in_sheets
    from iso_audit.reporting.tabular_report import schrijf_csv, schrijf_excel
    from iso_audit.store import verbinding

    logger.info("=== Report-only: bevindingen herladen uit DB (norm=%s) ===", norm)
    clause_map = laad_clause_map(norm)
    clausules = clause_map.get("clausules", {})

    conn = verbinding()
    rows = conn.execute("SELECT * FROM bevindingen ORDER BY clausule_id").fetchall()
    conn.close()

    if not rows:
        logger.error("Geen bevindingen in DB. Draai eerst de volledige pipeline.")
        sys.exit(1)

    bevindingen: list[dict[str, Any]] = [
        {
            "clausule": r["clausule_id"],
            "clausule_titel": clausules.get(r["clausule_id"], {}).get("titel", r["clausule_id"]),
            "document_naam": r["document_naam"] or "",
            "doc_id": r["doc_id"],
            "herkomst": r["herkomst"],
            "classificatie": r["classificatie"],
            "beschrijving": r["beschrijving"] or "",
            "onderbouwing": r["onderbouwing"] or "",
            "pre_classificatie": r["pre_classificatie"],
        }
        for r in rows
    ]
    logger.info("%d bevindingen geladen uit DB.", len(bevindingen))

    bevindingen, _ = _filter_ruis(bevindingen)

    llm_themas: dict[str, str] = {}
    if thema_llm:
        try:
            from iso_audit.classification.thema import verfijn_overig

            llm_themas = verfijn_overig(bevindingen)
        except Exception as e:
            logger.warning("LLM thema-verfijning mislukt (niet kritiek): %s", e)

    for i, bev in enumerate(bevindingen):
        bev_id = str(bev.get("id") or i)
        bev["_bev_id"] = bev_id
        bev["thema"] = llm_themas.get(bev_id) or bepaal_thema(bev)

    logger.info("Management summary genereren via Claude...")
    try:
        management_summary = _genereer_management_summary(bevindingen)
    except Exception as e:
        logger.error("Management summary mislukt: %s", e)
        sys.exit(1)

    pad = schrijf_rapport(bevindingen, [], [], management_summary, norm, scherpte=scherpte)
    logger.info("Lokaal rapport (md): %s", pad)

    _converteer_md_naar_html_docx_pdf(pad)

    try:
        csv_pad = schrijf_csv(bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas)
        xlsx_pad = schrijf_excel(bevindingen, norm, scherpte=scherpte, llm_themas=llm_themas)
        logger.info("Tabulair: %s  |  %s", csv_pad, xlsx_pad)
    except Exception as e:
        logger.warning("Tabulaire export mislukt (niet kritiek): %s", e)

    if os.environ.get("AUDIT_SHEETS_ID"):
        try:
            sheets_id = sla_op_in_sheets(bevindingen, [])
            logger.info("Sheets gesynchroniseerd: %s", sheets_id)
        except Exception as e:
            logger.warning("Sheets-sync mislukt: %s", e)


def main(argv: list[str] | None = None) -> None:
    """CLI-entrypoint voor de audit pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="ISO Audit Pipeline")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
        help="Toepasselijke norm (default: waarde van AUDIT_NORM in .env)",
    )
    parser.add_argument(
        "--setup-template",
        action="store_true",
        help="Maak het rapporttemplate aan in Drive (eenmalig)",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help=("Dry-run met synthetische testdata; geen Drive/Claude/Sheets-verbinding vereist"),
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Sla interactieve review over en accepteer alle Claude-classificaties",
    )
    parser.add_argument(
        "--write-sheets",
        action="store_true",
        help="Schrijf bevindingen naar Google Sheets (vereist gws auth login)",
    )
    parser.add_argument(
        "--scherpte",
        type=float,
        default=float(os.environ.get("AUDIT_SCHERPTE", "1.0")),
        metavar="0.0-1.0",
        help="Classificatie-scherpte: 1.0=strikt (default), 0.5=genuanceerd (PDCA)",
    )
    parser.add_argument(
        "--chapter",
        default=None,
        metavar="N",
        help="Beperk tot een hoofdstuk (bv. 4, 8, 5.1). Vermindert API-calls sterk.",
    )
    parser.add_argument(
        "--thema-llm",
        action="store_true",
        help=(
            "Verfijn thema-toekenning via LLM voor 'Overig'-findings (route B, enkele Haiku-calls)"
        ),
    )
    parser.add_argument(
        "--rehash",
        action="store_true",
        help=(
            "Ignoreer checkpoint en herclassificeer alle (doc, clausule, norm) combinaties (UPSERT)"
        ),
    )
    parser.add_argument(
        "--dry-run-cost",
        action="store_true",
        help=("Toon alleen kostenschatting van de classificatie-stap — geen API-calls voor LLM"),
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help=("Regenereer rapport vanuit bestaande bevindingen-DB — geen Drive/Miro/classificatie"),
    )
    args = parser.parse_args(argv)

    if args.local_only:
        run_local_only(args.norm)
    elif args.setup_template:
        _valideer_env()
        run_setup_template()
    elif args.report_only:
        run_report_only(args.norm, scherpte=args.scherpte, thema_llm=args.thema_llm)
    else:
        _valideer_env()
        run_audit(
            args.norm,
            no_review=args.no_review,
            write_sheets=args.write_sheets,
            chapter=args.chapter,
            scherpte=args.scherpte,
            thema_llm=args.thema_llm,
            rehash=args.rehash,
            dry_run_cost=args.dry_run_cost,
        )


if __name__ == "__main__":
    main()
