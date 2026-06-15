"""Tests voor `iso_audit.reporting.report_generation` — pure helpers + integratie."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.reporting import report_generation as rg


def _bev(klasse: str, clausule: str = "10.2", beschrijving: str = "x") -> dict[str, Any]:
    return {
        "classificatie": klasse,
        "clausule": clausule,
        "clausule_titel": "T",
        "beschrijving": beschrijving,
        "document_naam": "Doc",
        "herkomst": "Drive",
    }


# Volledige set placeholders voor management_summary_v1 (zie _management_summary_prompt).
_SUMMARY_VERVANGINGEN: dict[str, str] = {
    "management_context": "(context)",
    "nc_count": "2",
    "ofi_count": "1",
    "pos_count": "0",
    "top_nc_tekst": "(geen)",
    "top_ofi_tekst": "(geen)",
    "top_pos_tekst": "(geen)",
    "bridging_eis": "",
    "oordeel_zin": "De organisatie voldoet niet aan de norm.",
}


# ---------- _oordeel_zin / _oordeel_instructie ----------


def test_oordeel_zin_zonder_nc() -> None:
    assert rg._oordeel_zin(0) == "De organisatie voldoet aan de norm."


def test_oordeel_zin_met_nc() -> None:
    z = rg._oordeel_zin(3)
    assert "3" in z
    assert "non-conformiteiten" in z


def test_oordeel_instructie_zonder_nc() -> None:
    assert "Behoud" in rg._oordeel_instructie(0)


def test_oordeel_instructie_met_nc() -> None:
    assert "Vervang" in rg._oordeel_instructie(1)


# ---------- _overall_oordeel ----------


def test_overall_oordeel_voldoende() -> None:
    assert rg._overall_oordeel([_bev("OFI")]) == "voldoende"


def test_overall_oordeel_onvoldoende() -> None:
    assert rg._overall_oordeel([_bev("NC")]) == "onvoldoende"


# ---------- _top3_aanbevelingen ----------


def test_top3_aanbevelingen_leeg() -> None:
    assert rg._top3_aanbevelingen([]) == "Geen openstaande aanbevelingen."


def test_top3_aanbevelingen_prioriteert_nc() -> None:
    bev = [_bev("OFI"), _bev("NC"), _bev("OFI")]
    out = rg._top3_aanbevelingen(bev)
    # NC eerst.
    assert out.startswith("1. Clausule 10.2")
    # Drie regels.
    assert out.count("\n") == 2


# ---------- _groepeer_bevindingen ----------


def test_groepeer_norm_9001_filter() -> None:
    bev = [
        _bev("NC", "10.2"),  # 9001 / HLS-bereik 4-10
        _bev("OFI", "5.27"),  # 27001 Annex (start met 5 maar zit ook in 9001 range)
    ]
    # In de _groepeer-functie wordt clausule.startswith("4..10") gebruikt;
    # zowel 10.2 als 5.27 starten met cijfer 4-10, dus beide vallen in 9001-filter.
    out = rg._groepeer_bevindingen(bev, norm_filter="9001")
    assert "Clausule 10.2" in out
    assert "Clausule 5.27" in out


def test_groepeer_geen_bevindingen() -> None:
    """Lege input → fallback-tekst."""
    out = rg._groepeer_bevindingen([], norm_filter="9001")
    assert "Geen bevindingen" in out


# ---------- _bouw_placeholders ----------


def test_bouw_placeholders_bevat_alle_velden() -> None:
    bev = [_bev("NC"), _bev("OFI"), _bev("positief")]
    plh = rg._bouw_placeholders(bev, [], [], "9001", "Samenvatting hier.")
    # Tellingen kloppen.
    assert plh["totaal_nc"] == "1"
    assert plh["totaal_ofi"] == "1"
    assert plh["totaal_positief"] == "1"
    assert plh["overall_oordeel"] == "onvoldoende"
    assert plh["management_summary"] == "Samenvatting hier."
    assert plh["norm"] == "ISO 9001:2015"


def test_bouw_placeholders_lege_lijsten_fallback() -> None:
    plh = rg._bouw_placeholders([], [], [], "beide", "")
    assert "Geen ontbrekende clausules" in plh["ontbrekende_clausules"]
    assert "Geen items" in plh["handmatige_review_items"]


# ---------- _management_summary_prompt + _revise_summary_prompt ----------


def test_management_summary_prompt_bevat_cijfers() -> None:
    bev = [_bev("NC"), _bev("NC"), _bev("OFI")]
    prompt = rg._management_summary_prompt(bev)
    assert "Non-conformiteiten (NC): 2" in prompt
    assert "max 200 woorden" in prompt


def test_revise_summary_prompt_oordeel_instructie() -> None:
    """Oordeel-instructie staat in de revisie-prompt."""
    bev = [_bev("NC")]
    prompt = rg._revise_summary_prompt("Basis tekst.", bev)
    assert "Vervang het oordeel" in prompt


# ---------- _genereer_management_summary (mock anthropic) ----------


def _fake_anthropic_response(text: str) -> Any:
    block = MagicMock()
    block.text = text
    resp = MagicMock()
    resp.content = [block]
    return resp


def test_genereer_management_summary_data_modus(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIT_BASIS_SUMMARY", raising=False)
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_anthropic_response("Een samenvatting.")
    with patch.object(rg.anthropic, "Anthropic", return_value=fake_client):
        out = rg._genereer_management_summary([_bev("NC")])
    assert out == "Een samenvatting."


def test_genereer_management_summary_basis_pad_bestaat_niet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`AUDIT_BASIS_SUMMARY` op niet-bestaand pad → fallback data-modus."""
    monkeypatch.setenv("AUDIT_BASIS_SUMMARY", "/niet/bestaand/pad.md")
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_anthropic_response("Fallback.")
    with patch.object(rg.anthropic, "Anthropic", return_value=fake_client):
        out = rg._genereer_management_summary([_bev("OFI")])
    assert out == "Fallback."


# ---------- _check_verboden_woorden (deterministische gate) ----------


def test_check_verboden_woorden_schoon() -> None:
    schoon = "Leg de leveranciersafspraken vast in een register zodat dit aantoonbaar wordt."
    assert rg._check_verboden_woorden(schoon) == []


def test_check_verboden_woorden_detecteert() -> None:
    vuil = "De documentatie is onvoldoende en er ontbreekt een register; dit is een risico."
    gevonden = rg._check_verboden_woorden(vuil)
    assert gevonden == ["onvoldoende", "ontbreekt", "risico"] or set(gevonden) == {
        "onvoldoende",
        "ontbreekt",
        "risico",
    }


def test_check_verboden_woorden_woordgrens() -> None:
    """Samenstellingen als 'risicobeoordeling' mogen niet gevlagd worden."""
    assert rg._check_verboden_woorden("De risicobeoordeling is uitgevoerd.") == []


# ---------- _laad_prompt (versie-prompt loader) ----------


def test_laad_prompt_vult_placeholders() -> None:
    prompt = rg._laad_prompt("management_summary_v1", _SUMMARY_VERVANGINGEN)
    assert "Non-conformiteiten (NC): 2" in prompt
    assert "{{" not in prompt  # alle placeholders ingevuld
    assert "<!--" not in prompt  # redacteur-notitie gestript


def test_laad_prompt_faalt_op_ontbrekende_placeholder() -> None:
    with pytest.raises(ValueError, match="niet-ingevulde placeholder"):
        rg._laad_prompt("management_summary_v1", {"nc_count": "2"})


# ---------- _genereer_aanbevelingen (mock anthropic + gate) ----------


def test_genereer_aanbevelingen_leeg_zonder_llm() -> None:
    """Geen NC/OFI → geen LLM-call, vaste tekst."""
    with patch.object(rg.anthropic, "Anthropic") as fake:
        out = rg._genereer_aanbevelingen([_bev("positief")])
    assert out == "Geen openstaande aanbevelingen."
    fake.assert_not_called()


def test_genereer_aanbevelingen_draait_gate(caplog: pytest.LogCaptureFixture) -> None:
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_anthropic_response(
        "1. Documentatie is onvoldoende."  # bevat verboden woord
    )
    with patch.object(rg.anthropic, "Anthropic", return_value=fake_client):
        out = rg._genereer_aanbevelingen([_bev("NC")])
    assert "onvoldoende" in out
    assert "Verboden woord" in caplog.text  # gate logde de waarschuwing


# ---------- genereer_rapport (integratie) ----------


def test_genereer_rapport_zonder_template_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIT_TEMPLATE_DOC_ID", raising=False)
    with pytest.raises(OSError, match="AUDIT_TEMPLATE_DOC_ID"):
        rg.genereer_rapport([], [], [], "9001")


def test_genereer_rapport_volledige_flow() -> None:
    """copy → drive update → batchUpdate → docs get; mocked anthropic."""
    bev = [_bev("OFI")]
    gws_responses = [
        {"id": "new-doc"},  # drive files copy
        {},  # drive files update (folder move)
        {},  # docs batchUpdate
        {"body": {"content": []}},  # docs documents get
    ]
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_anthropic_response("Sum.")
    with (
        patch.object(rg, "_gws", side_effect=gws_responses) as mock_gws,
        patch.object(rg.anthropic, "Anthropic", return_value=fake_client),
    ):
        out = rg.genereer_rapport(
            bev, [], [], "9001", template_doc_id="tmpl-1", folder_id="folder-abc"
        )
    assert out == "new-doc"
    # 4 gws-calls verwacht.
    assert mock_gws.call_count == 4
