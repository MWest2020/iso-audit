"""Mode-implementaties: autonoom en integer.

Beide modes implementeren de :class:`iso_audit.modes.base.Mode` Protocol.
"""

from __future__ import annotations

from iso_audit.modes.autonoom import AutonoomMode
from iso_audit.modes.base import Decision, Mode, Risiconiveau
from iso_audit.modes.integer import IntegerMode

__all__ = ["AutonoomMode", "Decision", "IntegerMode", "Mode", "Risiconiveau"]
