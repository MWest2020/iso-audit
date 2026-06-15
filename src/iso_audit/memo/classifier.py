"""Selectie van NC's en verbeterpunten uit de findings-dataset.

Deterministisch en boring: geen LLM, geen verborgen heuristiek. NC's zijn de
findings met severity ``NC``. Verbeterpunten zijn expliciet gepromote OFI's,
aangevuld met OFI-clusters die een drempel overschrijden (één representant per
clausule).
"""

from __future__ import annotations

from collections import Counter

from iso_audit.memo.models import Finding


class DefaultClassifier:
    """Implementeert het ``FindingsClassifier``-protocol."""

    def ncs(self, findings: list[Finding]) -> list[Finding]:
        """Alle non-conformiteiten, in invoervolgorde."""
        return [f for f in findings if f.severity == "NC"]

    def improvements(self, findings: list[Finding], threshold: int) -> list[Finding]:
        """Verbeterpunten: expliciet gepromote OFI's + OFI-clusters >= ``threshold``.

        Per drempel-overschrijdende clausule wordt één representant (eerste in
        invoervolgorde) opgenomen, tenzij die clausule al via een expliciete
        promotie vertegenwoordigd is. Resultaat is stabiel en dedupliceert op id.
        """
        ofis = [f for f in findings if f.severity == "OFI"]
        gekozen: list[Finding] = []
        gezien_ids: set[str] = set()
        gedekte_clausules: set[str] = set()

        for f in ofis:
            if f.promote_to_improvement:
                gekozen.append(f)
                gezien_ids.add(f.id)
                gedekte_clausules.add(f.clause)

        if threshold > 0:
            tellingen = Counter(f.clause for f in ofis)
            drempel_clausules = {c for c, n in tellingen.items() if n >= threshold}
            for f in ofis:
                if (
                    f.clause in drempel_clausules
                    and f.clause not in gedekte_clausules
                    and f.id not in gezien_ids
                ):
                    gekozen.append(f)
                    gezien_ids.add(f.id)
                    gedekte_clausules.add(f.clause)

        return gekozen
