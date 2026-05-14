"""Tests voor `iso_audit.miro.interview` — pure helpers + factory-calls."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from iso_audit.miro import interview

# ---------- _vragen_voor_clausule ----------


def test_vragen_uit_bewijs_aantoon() -> None:
    """Items beginnend met 'Bewijs' of 'Aantoon' → 'Kun je ...?'."""
    nt = {"x.y": {"bewijslast": ["Bewijs van risicoanalyse"]}}
    vragen = interview._vragen_voor_clausule("x.y", "9001", nt)
    assert vragen == ["Kun je van risicoanalyse?"]


def test_vragen_aantoon_pad() -> None:
    nt = {"x.y": {"bewijslast": ["Aantoon dat training is gevolgd"]}}
    vragen = interview._vragen_voor_clausule("x.y", "9001", nt)
    assert vragen[0].startswith("Kun je")


def test_vragen_overig_geeft_heb_je_vraag() -> None:
    nt = {"x.y": {"bewijslast": ["Risicoregister actueel"]}}
    vragen = interview._vragen_voor_clausule("x.y", "9001", nt)
    assert vragen == ["Heb je risicoregister actueel? Kun je het laten zien?"]


def test_vragen_zonder_bewijslast_fallback() -> None:
    """Geen bewijslast → twee generieke fallback-vragen."""
    nt: dict[str, Any] = {"x.y": {}}
    vragen = interview._vragen_voor_clausule("x.y", "9001", nt)
    assert len(vragen) == 2
    assert "documentatie" in vragen[1].lower()


def test_vragen_onbekende_clausule_fallback() -> None:
    """Clausule niet in normteksten → fallback."""
    assert len(interview._vragen_voor_clausule("99.99", "9001", {})) == 2


# ---------- _uitnodiging_tekst ----------


def test_uitnodiging_tekst_bevat_alle_velden() -> None:
    tekst = interview._uitnodiging_tekst(
        "Interview 1", "Marleen", [("9001", "5.2"), ("27001", "5.11")]
    )
    assert "Interview 1" in tekst
    assert "Marleen" in tekst
    assert "9001 5.2" in tekst
    assert "27001 5.11" in tekst
    assert "45 minuten" in tekst


def test_uitnodiging_tekst_lege_clausules() -> None:
    """Lege clausules-lijst → tekst zonder regels-fout."""
    tekst = interview._uitnodiging_tekst("Interview X", "iemand", [])
    assert "Interview X" in tekst
    assert "Clausules:</strong> " in tekst


# ---------- _actieve_sessies ----------


def test_actieve_sessies_filtert_op_open(monkeypatch: Any) -> None:
    """Alleen sessies waarvan ≥1 clausule in `open_set` zit blijven."""
    monkeypatch.setattr(interview, "_open_clausules", lambda: {("9001", "5.2"), ("9001", "7.2")})
    sessies = interview._actieve_sessies()
    namen = [s[0] for s in sessies]
    assert "Interview 1 — Beleid & Strategie" in namen
    assert "Interview 2 — Ondersteuning & Competenties" in namen
    # Interview 3 (8.3) en 4 (27001 5.22) hebben geen open clausule.
    assert "Interview 3 — Ontwerp & Ontwikkeling" not in namen
    assert "Interview 4 — Leveranciersbeheer (27001)" not in namen


def test_actieve_sessies_clausules_subset(monkeypatch: Any) -> None:
    """Per actieve sessie blijven alleen de open clausules over."""
    monkeypatch.setattr(interview, "_open_clausules", lambda: {("9001", "7.2")})
    sessies = interview._actieve_sessies()
    sessie_2 = next(s for s in sessies if s[0].startswith("Interview 2"))
    assert sessie_2[2] == [("9001", "7.2")]
    # 7.3 is gedekt → niet meer in de sessie.


# ---------- factories ----------


def test_maak_frame_endpoint_en_dimensies() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "f-1"}
    interview._maak_frame("b1", "Test frame", x=100, y=200, client=client)
    endpoint, body = client.post.call_args.args[:2]
    assert endpoint == "/boards/b1/frames"
    assert body["geometry"]["width"] == interview.FRAME_W
    assert body["geometry"]["height"] == interview.FRAME_H
    assert body["position"] == {"x": 100, "y": 200, "origin": "center"}


def test_maak_tekstvak_endpoint() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "t-1"}
    interview._maak_tekstvak("b1", "tekst", 50, 60, 800, 200, client=client)
    endpoint, body = client.post.call_args.args[:2]
    assert endpoint == "/boards/b1/texts"
    assert body["data"]["content"] == "tekst"
    assert body["geometry"]["width"] == 800


def test_maak_sticky_kleur_en_endpoint() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "s-1"}
    interview._maak_sticky("b1", "vraag", 0, 0, interview.KLEUR_VRAGEN, client=client)
    endpoint, body = client.post.call_args.args[:2]
    assert endpoint == "/boards/b1/sticky_notes"
    assert body["style"]["fillColor"] == "light_blue"
    assert body["data"]["content"] == "vraag"


def test_factories_droog_passeert_door() -> None:
    """`droog=True` wordt doorgegeven aan `client.post`."""
    client = MagicMock()
    client.post.return_value = {"id": "dry-run"}
    interview._maak_frame("b1", "x", 0, 0, client=client, droog=True)
    assert client.post.call_args.kwargs["droog"] is True
