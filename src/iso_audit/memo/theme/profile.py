"""Profile-model + loader.

Een profiel is een standalone, overdraagbare YAML-bundle (geen externe
pad-refs). Kleurpalet heeft afgeleide defaults zodat een minimaal profiel
volstaat met primary + logo + org-naam. Loader: XDG-slug of absoluut pad,
``safe_load``, schema_version-check, SVG-validatie.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import BaseModel, Field, model_validator

from iso_audit.memo.theme.svg_validator import OnveiligeSvgError, valideer_svg

SCHEMA_VERSION = 1
_DEFAULT_FONT_STACK = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
_HEX = r"^#[0-9a-fA-F]{6}$"
HexColor = Annotated[str, Field(pattern=_HEX)]
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class ProfileError(ValueError):
    """Profiel kon niet geladen of gevalideerd worden."""


def _profiles_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "iso-audit" / "profiles"


def _tint(hex_kleur: str, factor: float = 0.06) -> str:
    """Meng ``hex_kleur`` met wit (factor = aandeel kleur) → lichte brand-tint."""
    r, g, b = (int(hex_kleur[i : i + 2], 16) for i in (1, 3, 5))
    mix = tuple(round(c * factor + 255 * (1 - factor)) for c in (r, g, b))
    return "#{:02x}{:02x}{:02x}".format(*mix)


class ColorPalette(BaseModel):
    primary: HexColor
    accent: HexColor | None = None
    muted: HexColor | None = None
    border: HexColor | None = None
    soft_bg: HexColor | None = None

    @model_validator(mode="after")
    def _vul_defaults(self) -> ColorPalette:
        self.accent = self.accent or self.primary
        self.muted = self.muted or "#6a6a6a"
        self.border = self.border or "#e0e4ec"
        self.soft_bg = self.soft_bg or _tint(self.primary)
        return self


class Organization(BaseModel):
    name: str
    legal_form: str | None = None


class Auditor(BaseModel):
    name: str
    role: str


class Brand(BaseModel):
    logo_svg: str
    colors: ColorPalette
    font_stack: str = _DEFAULT_FONT_STACK


class Defaults(BaseModel):
    language: str = "nl"
    include_independence_caveat: bool = False


class Profile(BaseModel):
    schema_version: int
    slug: str
    organization: Organization
    auditor: Auditor
    brand: Brand
    standards: list[str] = Field(default_factory=list)
    defaults: Defaults = Field(default_factory=Defaults)


def _valideer_policy(profiel: Profile) -> None:
    """Policy-gates die als ProfileError moeten propageren (niet via pydantic).

    Bewust buiten de pydantic-validator: een ValueError dáár wordt verpakt in een
    ValidationError en is niet als ProfileError vangbaar.
    """
    if profiel.schema_version != SCHEMA_VERSION:
        msg = (
            f"Profiel '{profiel.slug}' heeft schema_version {profiel.schema_version}; "
            f"deze tool ondersteunt alleen versie {SCHEMA_VERSION}. "
            "Migreer het profiel of gebruik een tool-versie die deze versie kent."
        )
        raise ProfileError(msg)
    try:
        valideer_svg(profiel.brand.logo_svg)
    except OnveiligeSvgError as exc:
        raise ProfileError(str(exc)) from exc


def _resolveer_pad(slug_or_path: str) -> Path:
    """Bepaal het YAML-pad uit een slug (XDG) of een expliciet pad."""
    if os.sep in slug_or_path or slug_or_path.startswith("~") or slug_or_path.endswith(".yaml"):
        pad = Path(slug_or_path).expanduser().resolve()
        if not pad.is_file():
            raise ProfileError(f"Profiel-pad bestaat niet: {pad}")
        return pad
    if not _SLUG_RE.match(slug_or_path):
        raise ProfileError(
            f"Ongeldige profiel-slug {slug_or_path!r}: alleen [a-z0-9_-], geen pad-segmenten."
        )
    base = _profiles_dir().resolve()
    pad = (base / f"{slug_or_path}.yaml").resolve()
    if base not in pad.parents:
        raise ProfileError(f"Profiel-slug resolveert buiten {base} — geweigerd.")
    if not pad.is_file():
        raise ProfileError(f"Profiel '{slug_or_path}' niet gevonden in {base}.")
    return pad


def laad_profiel(slug_or_path: str) -> Profile:
    """Laad + valideer een profiel uit XDG-slug of absoluut/relatief pad."""
    pad = _resolveer_pad(slug_or_path)
    data: Any = yaml.safe_load(pad.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProfileError(f"Profiel {pad} bevat geen geldige YAML-mapping.")
    profiel = Profile(**data)
    _valideer_policy(profiel)
    return profiel


def opslaan_profiel(profiel: Profile, *, overschrijf: bool = False) -> Path:
    """Schrijf een profiel naar de XDG-locatie ``<slug>.yaml``."""
    _valideer_policy(profiel)
    base = _profiles_dir()
    base.mkdir(parents=True, exist_ok=True)
    pad = base / f"{profiel.slug}.yaml"
    if pad.exists() and not overschrijf:
        raise ProfileError(f"Profiel {pad} bestaat al; gebruik overschrijf=True.")
    pad.write_text(
        yaml.safe_dump(profiel.model_dump(), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return pad
