"""HTML-rendering van de auditmemo via Jinja2.

Laadt de ``management-memo``-templates en injecteert het profiel (palette,
font-stack, logo) plus het samengestelde :class:`AuditMemo`-model. Autoescape
staat aan; alleen expliciet veilige velden (rich tekst, logo) gebruiken ``|safe``.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from iso_audit.memo.models import AuditMemo
from iso_audit.memo.theme.profile import Profile

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_MEMO_TEMPLATE = "management-memo/memo.html.j2"


class MemoRendererImpl:
    """Implementeert het ``MemoRenderer``-protocol (HTML + PDF)."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_html(self, memo: AuditMemo, profile: Profile) -> str:
        """Render de memo naar een self-contained HTML-string."""
        template = self._env.get_template(_MEMO_TEMPLATE)
        return template.render(memo=memo, profile=profile, colors=profile.brand.colors)

    def render_pdf(self, html: str, output: Path) -> None:
        """Render een HTML-string naar PDF. Importeert WeasyPrint lazy."""
        from iso_audit.memo.renderer.pdf import schrijf_pdf

        schrijf_pdf(html, output)
