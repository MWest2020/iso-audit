"""Auditmemo-generatie — management one-pager uit de findings-dataset.

Genereert de management-auditmemo (HTML + PDF) uit findings + norm-database +
profiel, met de vastgelegde memo-structuur. Multi-tenant via profielen; normen
als plug-in YAML. Zie ``openspec/changes/auditmemo-management/`` en
``docs/memo-architecture.md``.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
