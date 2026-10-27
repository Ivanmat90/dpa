"""Глобальные флаги запуска (--dry-run, --yes)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Options:
    dry_run: bool = False
    assume_yes: bool = False


OPTS = Options()
