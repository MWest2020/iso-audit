"""Tests voor de profiel-wizard (`iso_audit.memo.theme.elicitation`)."""

from __future__ import annotations

import pytest

from iso_audit.memo.theme.elicitation import run_wizard, slugify
from iso_audit.memo.theme.svg_validator import OnveiligeSvgError

_LOGO = '<svg viewBox="0 0 10 10"><path d="M0 0h10v10z"/></svg>'


def test_slugify() -> None:
    assert slugify("Conduction B.V.") == "conduction-b-v"
    assert slugify("  ") == "profiel"


class _Antwoorden:
    """Scripted ask/confirm op basis van een dict prompt→antwoord."""

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def ask(self, text: str, default: str | None = None) -> str:
        return self.mapping.get(text, default if default is not None else "")


def test_run_wizard_bouwt_geldig_profiel() -> None:
    a = _Antwoorden(
        {
            "Organisatienaam": "Conduction B.V.",
            "Pad naar logo-SVG-bestand": "/x/logo.svg",
            "Primaire kleur (hex, bv. #4376fc)": "#4376fc",
            "Auditor-naam": "Mark",
        }
    )
    profiel = run_wizard(
        ask=a.ask,
        ask_confirm=lambda text, default=False: True,
        read_file=lambda _pad: _LOGO,
    )
    assert profiel.slug == "conduction-b-v"
    assert profiel.organization.name == "Conduction B.V."
    assert profiel.auditor.role == "ISO-auditor"  # default
    assert profiel.brand.colors.accent == "#4376fc"  # afgeleid
    assert profiel.defaults.include_independence_caveat is True
    assert profiel.standards == ["iso-9001-2015", "iso-27001-2022"]


def test_run_wizard_weigert_onveilige_svg() -> None:
    a = _Antwoorden(
        {
            "Organisatienaam": "X",
            "Primaire kleur (hex, bv. #4376fc)": "#000000",
            "Auditor-naam": "Y",
        }
    )
    with pytest.raises(OnveiligeSvgError):
        run_wizard(
            ask=a.ask,
            ask_confirm=lambda text, default=False: False,
            read_file=lambda _pad: "<svg><script>x</script></svg>",
        )
