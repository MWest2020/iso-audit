"""Generieke ingest via het `Source`-Protocol → pipeline-document-dicts.

Brug tussen de pluggable Source-adapters (`list_documents` + `fetch_content`)
en de bestaande pipeline, die met document-dicts werkt (zelfde shape als
`DriveSource.haal_documenten_op`). Hierdoor kan `run_audit` elke geselecteerde
bron (Jira, Planning, … en straks GitHub/Codeberg) inlezen — niet alleen de
historisch hardcoded Drive + Miro.

Boring & auditable: één pure-genoeg functie die per Document één dict bouwt;
leesfouten op één document zijn nooit fataal (gelogd + overgeslagen).
"""

from __future__ import annotations

import logging
from typing import Any

from iso_audit import sources

logger = logging.getLogger(__name__)


def ingest_documenten(naam: str) -> list[dict[str, Any]]:
    """Lees alle documenten van bron ``naam`` in als pipeline-document-dicts.

    Mapt elk ``Document`` (+ ``fetch_content``) naar de dict-shape die
    ``koppel_documenten`` / ``classificeer_alle_bevindingen`` verwachten::

        {"naam", "id", "mime_type", "tekst", "herkomst", "modified_at"}

    ``herkomst`` is de bronnaam met hoofdletter (``"jira"`` → ``"Jira"``) en
    wordt zo in de ``bevindingen``-tabel vastgelegd, zodat een bevinding terug
    te voeren is op zijn bron. Documenten die niet leesbaar zijn worden
    overgeslagen (gelogd), nooit fataal.

    :raises KeyError: als ``naam`` geen geregistreerde Source-adapter is.
    """
    adapter = sources.get(naam)()
    herkomst = naam.capitalize()
    docs: list[dict[str, Any]] = []
    for d in adapter.list_documents():
        try:
            tekst = adapter.fetch_content(d)
        except Exception as e:  # één onleesbaar document mag de run niet breken
            logger.warning("Bron %s: kon document %r niet lezen: %s", naam, d.id, e)
            continue
        docs.append(
            {
                "naam": d.titel,
                "id": d.id,
                "mime_type": d.type or "",
                "tekst": tekst,
                "herkomst": herkomst,
                "modified_at": d.laatst_gewijzigd or None,
            }
        )
    logger.info("Bron %s: %d document(en) ingelezen via Source-Protocol", naam, len(docs))
    return docs
