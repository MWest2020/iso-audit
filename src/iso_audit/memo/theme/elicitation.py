"""First-run wizard: bouw een profiel interactief.

IO is injecteerbaar (``ask`` / ``ask_confirm`` / ``read_file``) zodat de flow
testbaar is zonder echte terminal. ``profile new`` roept ``run_wizard`` met de
echte Typer-IO aan en slaat het resultaat op.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from iso_audit.memo.theme.profile import (
    Auditor,
    Brand,
    ColorPalette,
    Defaults,
    Organization,
    Profile,
)
from iso_audit.memo.theme.svg_validator import valideer_svg

AskFn = Callable[..., str]
ConfirmFn = Callable[..., bool]
ReadFn = Callable[[str], str]

_SLUG_NIET = re.compile(r"[^a-z0-9_-]+")


def slugify(naam: str) -> str:
    """Maak een geldige profiel-slug van een vrije naam."""
    slug = _SLUG_NIET.sub("-", naam.strip().lower()).strip("-")
    return slug or "profiel"


def _lees_bestand(pad: str) -> str:
    return Path(pad).expanduser().read_text(encoding="utf-8")


def run_wizard(
    *,
    ask: AskFn,
    ask_confirm: ConfirmFn,
    read_file: ReadFn = _lees_bestand,
) -> Profile:
    """Doorloop de 8 stappen en geef een gevalideerd :class:`Profile` terug."""
    org_naam = ask("Organisatienaam")
    slug = slugify(ask("Profiel-slug", default=slugify(org_naam)))

    logo_pad = ask("Pad naar logo-SVG-bestand")
    logo_svg = read_file(logo_pad)
    valideer_svg(logo_svg)  # vroege, duidelijke fout bij onveilige SVG

    primary = ask("Primaire kleur (hex, bv. #4376fc)")
    auditor_naam = ask("Auditor-naam")
    auditor_rol = ask("Auditor-rol", default="ISO-auditor")
    standaarden_ruw = ask(
        "ISO-standaarden in scope (komma-gescheiden slugs)",
        default="iso-9001-2015,iso-27001-2022",
    )
    standaarden = [s.strip() for s in standaarden_ruw.split(",") if s.strip()]
    taal = ask("Default taal (nl/en)", default="nl")
    onafhankelijkheid = ask_confirm(
        "Auditor-onafhankelijkheid-voorbehoud standaard opnemen?", default=False
    )

    return Profile(
        schema_version=1,
        slug=slug,
        organization=Organization(name=org_naam),
        auditor=Auditor(name=auditor_naam, role=auditor_rol),
        brand=Brand(logo_svg=logo_svg, colors=ColorPalette(primary=primary)),
        standards=standaarden,
        defaults=Defaults(language=taal, include_independence_caveat=onafhankelijkheid),
    )
