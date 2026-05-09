"""Console-script entry-point voor iso-audit.

Volledige CLI-functionaliteit (subcommands ``pipeline``, ``doctor``,
``setup-template``) komt in milestone B. In milestone A is dit een stub
zodat ``iso-audit --help`` werkt en de entry-point in ``pyproject.toml``
geldig is.
"""

from __future__ import annotations

import argparse
import sys

from iso_audit import __version__


def main(argv: list[str] | None = None) -> int:
    """Hoofdingang voor de ``iso-audit`` console-script.

    Returnt een exit-code (``0`` succes, ``2`` argument-fout).
    """
    parser = argparse.ArgumentParser(
        prog="iso-audit",
        description="ISO 9001 + 27001 audit pipeline (milestone A skeleton).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["pipeline", "doctor", "setup-template"],
        help="Subcommand to run (komt in milestone B).",
    )

    args = parser.parse_args(argv)

    if args.subcommand is None:
        parser.print_help()
        return 0

    print(
        f"iso-audit {args.subcommand!r} is nog niet geïmplementeerd in milestone A. "
        "Zie openspec/changes/iso-refactor/tasks.md voor de roadmap.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
