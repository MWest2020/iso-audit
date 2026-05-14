"""Tests voor `iso_audit.cli` — subcommands + `--source` flag."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from iso_audit import cli

# ---------- --version / --help / geen subcommand ----------


def test_version_flag_print_versie(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "iso-audit" in out


def test_geen_subcommand_geeft_argparse_error() -> None:
    """argparse `required=True` op subparser → SystemExit(2)."""
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == 2


# ---------- _resolve_sources ----------


def test_resolve_sources_cli_eerst(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(cli._SOURCE_ENV_VAR, "miro")
    out = cli._resolve_sources(["drive"])
    assert out == ["drive"]


def test_resolve_sources_env_fallback(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv(cli._SOURCE_ENV_VAR, "drive,miro")
    with caplog.at_level("INFO"):
        out = cli._resolve_sources(None)
    assert out == ["drive", "miro"]
    assert any("fallback naar" in r.message for r in caplog.records)


def test_resolve_sources_geen_input_exit_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv(cli._SOURCE_ENV_VAR, raising=False)
    with pytest.raises(SystemExit) as exc:
        cli._resolve_sources(None)
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "verplicht" in err


def test_resolve_sources_onbekend_exit_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv(cli._SOURCE_ENV_VAR, raising=False)
    with pytest.raises(SystemExit) as exc:
        cli._resolve_sources(["bogus"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "onbekend" in err.lower()


def test_resolve_sources_multi_dedup_sort(monkeypatch: pytest.MonkeyPatch) -> None:
    out = cli._resolve_sources(["miro", "drive", "drive"])
    assert out == ["drive", "miro"]


# ---------- pipeline subcommand ----------


def test_pipeline_zonder_source_faalt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv(cli._SOURCE_ENV_VAR, raising=False)
    with pytest.raises(SystemExit) as exc:
        cli.main(["pipeline", "--norm", "9001"])
    assert exc.value.code == 2


def test_pipeline_met_source_roept_run_audit_aan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(cli._SOURCE_ENV_VAR, raising=False)
    with patch("iso_audit.pipeline.run_audit") as mock_audit:
        rc = cli.main(["pipeline", "--source", "drive", "--norm", "9001"])
    assert rc == 0
    mock_audit.assert_called_once()


def test_pipeline_env_source_fallback_werkt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(cli._SOURCE_ENV_VAR, "drive")
    with patch("iso_audit.pipeline.run_audit") as mock_audit:
        cli.main(["pipeline", "--norm", "27001"])
    mock_audit.assert_called_once()


def test_pipeline_no_review_flag_door_gegeven() -> None:
    with patch("iso_audit.pipeline.run_audit") as mock_audit:
        cli.main(["pipeline", "--source", "drive", "--no-review", "--rehash"])
    kw = mock_audit.call_args.kwargs
    assert kw["no_review"] is True
    assert kw["rehash"] is True


# ---------- doctor subcommand ----------


def test_doctor_zonder_gws_exit_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _: None)
    rc = cli.main(["doctor"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "[fail]" in out


def test_doctor_met_gws_exit_0(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _: "/usr/bin/gws")
    rc = cli.main(["doctor"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "Geregistreerde sources" in out


# ---------- setup-template subcommand ----------


def test_setup_template_roept_pipeline_helpers_aan() -> None:
    with (
        patch("iso_audit.pipeline._valideer_env") as mock_env,
        patch("iso_audit.pipeline.run_setup_template") as mock_setup,
    ):
        rc = cli.main(["setup-template"])
    assert rc == 0
    mock_env.assert_called_once()
    mock_setup.assert_called_once()


# ---------- __main__ delegatie ----------


def test_main_module_delegeert(monkeypatch: pytest.MonkeyPatch) -> None:
    """`python -m iso_audit` importeert __main__ en roept cli.main aan."""
    from iso_audit import __main__ as iso_main

    assert iso_main.main is cli.main
