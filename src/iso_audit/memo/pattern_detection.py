"""Cross-clause patroondetectie voor de NC-context.

Maakt expliciet wanneer een clausule zowel positieve bevindingen als OFI's
heeft — het patroon "de praktijk werkt, maar de vastlegging is gefragmenteerd"
dat de auditor-spiegel zichtbaar wil maken. Deterministisch, op basis van
tellingen; de inhoudelijke duiding komt uit de finding-beschrijving.
"""

from __future__ import annotations

from iso_audit.memo.models import Finding


class DefaultPatternDetector:
    """Implementeert het ``PatternDetector``-protocol."""

    def pattern_note(self, clause: str, findings: list[Finding]) -> str | None:
        """Genereer een patroon-zin als de clausule zowel positief als OFI scoort.

        Geeft ``None`` als het patroon niet van toepassing is (geen gemengd beeld).
        """
        positief = sum(1 for f in findings if f.clause == clause and f.severity == "POSITIVE")
        ofi = sum(1 for f in findings if f.clause == clause and f.severity == "OFI")
        if positief == 0 or ofi == 0:
            return None

        pos_woord = "bevinding" if positief == 1 else "bevindingen"
        ofi_woord = "OFI" if ofi == 1 else "OFI's"
        return (
            f"De praktijk op clausule {clause} werkt deels aantoonbaar "
            f"({positief} positieve {pos_woord} op deze clausule), maar de "
            f"vastlegging is gefragmenteerd ({ofi} {ofi_woord} op dezelfde clausule)."
        )
