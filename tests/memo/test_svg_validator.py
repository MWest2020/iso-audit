"""Tests voor `iso_audit.memo.theme.svg_validator`."""

from __future__ import annotations

import pytest

from iso_audit.memo.theme.svg_validator import OnveiligeSvgError, valideer_svg

_SCHOON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0h10v10H0z"/></svg>'
)


def test_schone_svg_passeert() -> None:
    valideer_svg(_SCHOON)  # mag niet gooien


@pytest.mark.parametrize(
    "svg",
    [
        "<svg><script>alert(1)</script></svg>",
        "<svg><foreignObject><div/></foreignObject></svg>",
        '<svg><image href="https://evil.example/x.png"/></svg>',
        '<svg><image xlink:href="file:///etc/passwd"/></svg>',
        '<svg onload="alert(1)"></svg>',
        '<svg><a href="javascript:alert(1)">x</a></svg>',
        '<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg>&x;</svg>',
    ],
)
def test_onveilige_svg_geweigerd(svg: str) -> None:
    with pytest.raises(OnveiligeSvgError):
        valideer_svg(svg)


def test_niet_svg_geweigerd() -> None:
    with pytest.raises(OnveiligeSvgError):
        valideer_svg("<html><body>geen svg</body></html>")
