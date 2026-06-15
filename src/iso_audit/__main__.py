"""Maakt ``python -m iso_audit`` werkbaar — delegeert naar cli.main."""

from __future__ import annotations

from iso_audit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
