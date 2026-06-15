"""Tests voor `iso_audit.memo.theme.profile`."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from iso_audit.memo.theme.profile import (
    Profile,
    ProfileError,
    laad_profiel,
    opslaan_profiel,
)

_LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0h10v10z"/></svg>'


def _minimaal(slug: str = "conduction", versie: int = 1) -> dict:
    return {
        "schema_version": versie,
        "slug": slug,
        "organization": {"name": "Conduction B.V."},
        "auditor": {"name": "Mark", "role": "ISO-auditor"},
        "brand": {"logo_svg": _LOGO, "colors": {"primary": "#4376fc"}},
    }


def test_minimaal_profiel_leidt_kleuren_af() -> None:
    p = Profile(**_minimaal())
    c = p.brand.colors
    assert c.accent == "#4376fc"  # default = primary
    assert c.muted == "#6a6a6a"
    assert c.border == "#e0e4ec"
    assert c.soft_bg is not None and c.soft_bg.startswith("#")  # afgeleide tint
    assert p.brand.font_stack.startswith("-apple-system")


def test_ongeldige_hex_geweigerd() -> None:
    data = _minimaal()
    data["brand"]["colors"]["primary"] = "blauw"
    with pytest.raises(ValidationError):
        Profile(**data)


def test_laad_schema_versie_2_faalt(tmp_path: Path) -> None:
    pad = tmp_path / "p.yaml"
    pad.write_text(yaml.safe_dump(_minimaal(versie=2)), encoding="utf-8")
    with pytest.raises(ProfileError, match="schema_version"):
        laad_profiel(str(pad))


def test_laad_onveilige_svg_faalt(tmp_path: Path) -> None:
    data = _minimaal()
    data["brand"]["logo_svg"] = "<svg><script>x</script></svg>"
    pad = tmp_path / "p.yaml"
    pad.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ProfileError):
        laad_profiel(str(pad))


def test_ongeldige_slug_geweigerd() -> None:
    with pytest.raises(ProfileError, match="slug"):
        laad_profiel("foo.bar")  # punt → geen geldige slug, geen pad


def test_opslaan_en_laden_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    p = Profile(**_minimaal())
    pad = opslaan_profiel(p)
    assert pad.is_file()
    geladen = laad_profiel("conduction")
    assert geladen.organization.name == "Conduction B.V."
    assert geladen.brand.colors.accent == "#4376fc"
