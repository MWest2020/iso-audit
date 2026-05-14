"""Console-script entry-point voor iso-audit.

Subcommands (§2.6.1):

- ``pipeline``       — voer de volledige audit-pipeline uit
- ``doctor``         — controleer of de omgeving correct geconfigureerd is
- ``setup-template`` — eenmalige Drive-template-aanmaak

Verder:

- ``--source`` flag (§2.6.2): verplicht voor ``pipeline``, multi-value,
  met ``ISO_AUDIT_DEFAULT_SOURCE``-env-var-fallback (INFO-log bij
  fallback). Voor ``setup-template`` en ``doctor`` is ``--source`` niet
  relevant.

``iso_audit.__main__`` en directe ``python -m iso_audit.pipeline``-call
delegeren beide naar deze ``main()``.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys

from iso_audit import __version__

logger = logging.getLogger(__name__)

_SOURCE_ENV_VAR = "ISO_AUDIT_DEFAULT_SOURCE"


def _bekende_bronnen() -> list[str]:
    """Alle ingest-bronnen die de pipeline accepteert."""
    from iso_audit.ingest import beschikbare_bronnen

    return beschikbare_bronnen()


def _resolve_sources(args_sources: list[str] | None) -> list[str]:
    """Bepaal de actieve source-set uit CLI of `ISO_AUDIT_DEFAULT_SOURCE`-env.

    Returnt een gesorteerde, deduplicate lijst.
    Raises `SystemExit(2)` als er geen sources zijn opgegeven of als een
    onbekende source genoemd wordt.
    """
    bekende = set(_bekende_bronnen())

    sources: list[str]
    if args_sources:
        sources = list(args_sources)
    else:
        env_val = os.environ.get(_SOURCE_ENV_VAR, "").strip()
        if not env_val:
            print(
                f"iso-audit: --source is verplicht (of zet {_SOURCE_ENV_VAR}). "
                f"Beschikbare bronnen: {sorted(bekende)}.",
                file=sys.stderr,
            )
            raise SystemExit(2)
        sources = [s.strip() for s in env_val.split(",") if s.strip()]
        logger.info("--source niet opgegeven; fallback naar %s=%s", _SOURCE_ENV_VAR, env_val)

    onbekend = [s for s in sources if s not in bekende]
    if onbekend:
        print(
            f"iso-audit: onbekende source(s) {onbekend}. Beschikbare: {sorted(bekende)}.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    return sorted(set(sources))


def _run_pipeline(args: argparse.Namespace) -> int:
    from iso_audit import pipeline

    sources = _resolve_sources(args.source)
    logger.info("Actieve sources: %s", sources)

    pipeline.run_audit(
        args.norm,
        no_review=args.no_review,
        write_sheets=args.write_sheets,
        chapter=args.chapter,
        scherpte=args.scherpte,
        thema_llm=args.thema_llm,
        rehash=args.rehash,
        dry_run_cost=args.dry_run_cost,
    )
    return 0


def _run_setup_template(_args: argparse.Namespace) -> int:
    from iso_audit import pipeline

    pipeline._valideer_env()
    pipeline.run_setup_template()
    return 0


def _run_doctor(_args: argparse.Namespace) -> int:
    """Check of de omgeving correct is geconfigureerd."""
    ok = True

    if shutil.which("gws"):
        print("[ok]  gws CLI gevonden in PATH")
    else:
        print("[fail] gws CLI niet gevonden in PATH")
        ok = False

    sleutels = [
        "AUDIT_NORM",
        "AUDIT_DB_PATH",
        "AUDIT_DRIVE_FOLDER_ID",
        "ANTHROPIC_API_KEY",
        "MIRO_BOARD_ID",
    ]
    print()
    print("Omgevingsvariabelen:")
    for k in sleutels:
        v = os.environ.get(k, "")
        getoond = "[set]" if v else "[leeg]"
        print(f"  {k:<25} {getoond}")

    print()
    bronnen = _bekende_bronnen()
    print(f"Geregistreerde sources: {bronnen}")

    return 0 if ok else 1


def _voeg_pipeline_args_toe(parser: argparse.ArgumentParser) -> None:
    """Pipeline-specifieke argumenten."""
    parser.add_argument(
        "--source",
        action="append",
        default=None,
        help=(
            "Source-adapter(s) om uit te lezen. Meerdere keren opgeven mag. "
            f"Fallback: env-var {_SOURCE_ENV_VAR} (komma-gescheiden)."
        ),
    )
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
        help="Toepasselijke norm (default: waarde van AUDIT_NORM in .env)",
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
        help="Classificatie-scherpte: 1.0=strikt (default), 0.5=genuanceerd",
    )
    parser.add_argument(
        "--chapter",
        default=None,
        metavar="N",
        help="Beperk tot een hoofdstuk (bv. 4, 8, 5.1).",
    )
    parser.add_argument(
        "--thema-llm",
        action="store_true",
        help="Verfijn thema-toekenning via LLM voor 'Overig'-findings",
    )
    parser.add_argument(
        "--rehash",
        action="store_true",
        help="Ignoreer checkpoint en herclassificeer alles (UPSERT)",
    )
    parser.add_argument(
        "--dry-run-cost",
        action="store_true",
        help="Toon alleen kostenschatting — geen API-calls voor LLM",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iso-audit",
        description="ISO 9001 + 27001 audit pipeline.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_pipe = sub.add_parser("pipeline", help="Voer de auditpipeline uit")
    _voeg_pipeline_args_toe(p_pipe)
    p_pipe.set_defaults(func=_run_pipeline)

    p_doc = sub.add_parser("doctor", help="Controleer omgeving en configuratie")
    p_doc.set_defaults(func=_run_doctor)

    p_tmpl = sub.add_parser("setup-template", help="Maak het Drive-template eenmalig aan")
    p_tmpl.set_defaults(func=_run_setup_template)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Hoofdingang voor de ``iso-audit`` console-script.

    Returnt een exit-code (``0`` succes, ``2`` argument-fout).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
