"""Данные для TUI. Чистый Python, без Textual - поэтому покрыт тестами."""
from __future__ import annotations

import platform
from typing import Dict, List, Optional, Tuple

from .. import __version__, aliases, config
from ..backends import distro_info, kernel
from ..backends.base import Backend, PackageHit
from ..db import Database
from ..i18n import get_language

MAX_RESULTS = 400


def rank(query: str, name: str) -> int:
    q, n = query.lower(), name.lower()
    if n == q:
        return 0
    if n.startswith(q):
        return 1
    if q in n:
        return 2
    return 3


class TuiModel:
    def __init__(self, backend: Backend, db: Database):
        self.backend = backend
        self.db = db
        self._installed: Optional[Dict[str, str]] = None

    @property
    def pm(self) -> str:
        return self.backend.name

    # --- пакеты ---
    def installed(self, refresh: bool = False) -> Dict[str, str]:
        if self._installed is None or refresh:
            self._installed = self.backend.installed_packages()
        return self._installed

    def invalidate(self) -> None:
        self._installed = None

    def search(self, query: str) -> List[PackageHit]:
        query = query.strip()
        if not query:
            return []
        hits = self.backend.search_hits(query)
        installed = self.installed()
        for hit in hits:
            version = installed.get(hit.name)
            if version is not None:
                hit.installed = True
                hit.version = hit.version or version
        hits.sort(key=lambda h: rank(query, h.name))  # sort стабилен
        return hits[:MAX_RESULTS]

    def info(self, name: str) -> str:
        return self.backend.info_text(name)

    # --- система ---
    def system_info(self) -> List[Tuple[str, str]]:
        d = distro_info()
        return [("distribution", d.name), ("pm", self.pm.upper()),
                ("kernel", kernel()), ("arch", platform.machine()),
                ("python", platform.python_version()), ("dpa", __version__),
                ("language", get_language()),
                ("config", str(config.config_dir())),
                ("data", str(config.data_dir()))]

    def history(self, limit: int = 200) -> List[Dict]:
        return self.db.history(limit)

    # --- алиасы ---
    def alias_rows(self) -> List[Tuple[str, str, str]]:
        rows = [(a, r, "custom") for a, r in self.db.list_aliases(self.pm)]
        for name in sorted(aliases.BUILTIN):
            targets = aliases.builtin_for(name, self.pm)
            if targets:
                rows.append((name, " ".join(targets), "builtin"))
        return rows

    def add_alias(self, alias: str, target: str) -> bool:
        parts = target.split()
        if not aliases.valid_name(alias) or not parts or \
                not all(aliases.valid_name(p) for p in parts):
            return False
        self.db.add_alias(alias, " ".join(parts), self.pm)
        return True

    def remove_alias(self, alias: str) -> bool:
        return self.db.remove_alias(alias, self.pm)
