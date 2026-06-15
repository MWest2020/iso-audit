"""Veiligheidsvalidatie voor inline SVG-logo's.

Een profiel draagt zijn logo als inline SVG-string. Omdat die string ongewijzigd
in HTML/PDF terechtkomt, weigeren we constructies die code uitvoeren of externe
bronnen laden. Boring & auditable: expliciete blocklist, harde fout bij een hit.
"""

from __future__ import annotations

import re

# (patroon, leesbare reden) — alle case-insensitive.
_VERBODEN: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"<\s*script", re.I), "<script>"),
    (re.compile(r"<\s*foreignObject", re.I), "<foreignObject>"),
    (
        re.compile(r"<\s*image\b[^>]*\b(?:xlink:)?href\s*=\s*['\"]?\s*(?:https?:|file:|//)", re.I),
        "externe <image>-referentie",
    ),
    (re.compile(r"javascript:", re.I), "javascript:-URI"),
    (re.compile(r"<!ENTITY", re.I), "externe XML-entity"),
    (re.compile(r"\son\w+\s*=", re.I), "inline event-handler (on...=)"),
)


class OnveiligeSvgError(ValueError):
    """Een SVG bevat een verboden, onveilige constructie."""


def valideer_svg(svg: str) -> None:
    """Weiger een SVG met onveilige constructies; doe niets als hij schoon is.

    Raises:
        OnveiligeSvgError: bij script/foreignObject/externe-image/event-handler/
            javascript-URI/externe-entity, of als de string geen ``<svg`` bevat.
    """
    if "<svg" not in svg.lower():
        msg = "Profiel-logo is geen SVG (geen <svg>-element gevonden)."
        raise OnveiligeSvgError(msg)
    for patroon, reden in _VERBODEN:
        if patroon.search(svg):
            msg = f"Onveilige SVG geweigerd: {reden} is niet toegestaan in een profiel-logo."
            raise OnveiligeSvgError(msg)
