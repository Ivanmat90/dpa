"""Общий интерфейс бэкендов. Каждый бэкенд только описывает команды."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .. import ui
from ..i18n import t
from ..runtime import run


@dataclass
class PackageHit:
    """Результат поиска для TUI."""
    name: str
    version: str = ""
    description: str = ""
    installed: bool = False


class Backend:
    name = ""
    PRIVILEGED = frozenset({"install", "remove", "upgrade", "clean",
                            "autoremove", "refresh"})
    refresh_ok_codes: Tuple[int, ...] = (0,)

    # --- описание команд (без sudo) ---
    def cmd_install(self, pkgs: Sequence[str], yes: bool) -> List[str]:
        raise NotImplementedError

    def cmd_remove(self, pkgs: Sequence[str], yes: bool) -> List[str]:
        raise NotImplementedError

    def cmd_refresh(self) -> List[str]:
        raise NotImplementedError

    def cmd_upgrade(self, yes: bool) -> List[str]:
        raise NotImplementedError

    def cmd_search(self, query: str) -> List[str]:
        raise NotImplementedError

    def cmd_info(self, pkg: str) -> List[str]:
        raise NotImplementedError

    def cmd_list(self) -> List[str]:
        raise NotImplementedError

    def cmd_clean(self, yes: bool) -> List[str]:
        raise NotImplementedError

    def cmd_autoremove(self, yes: bool) -> List[str]:
        raise NotImplementedError

    # --- выполнение ---
    def _exec(self, op: str, argv: List[str], ok_codes=(0,)) -> bool:
        return run(argv, privileged=op in self.PRIVILEGED, ok_codes=ok_codes).ok

    def install(self, pkgs: Sequence[str], yes: bool = False) -> bool:
        return self._exec("install", self.cmd_install(pkgs, yes))

    def remove(self, pkgs: Sequence[str], yes: bool = False) -> bool:
        return self._exec("remove", self.cmd_remove(pkgs, yes))

    def refresh(self) -> bool:
        return self._exec("refresh", self.cmd_refresh(), self.refresh_ok_codes)

    def upgrade(self, yes: bool = False) -> bool:
        return self._exec("upgrade", self.cmd_upgrade(yes))

    def search(self, query: str) -> bool:
        return self._exec("search", self.cmd_search(query))

    def info(self, pkg: str) -> bool:
        return self._exec("info", self.cmd_info(pkg))

    def clean(self, yes: bool = False) -> bool:
        return self._exec("clean", self.cmd_clean(yes))

    def autoremove(self, yes: bool = False) -> bool:
        return self._exec("autoremove", self.cmd_autoremove(yes))

    def list_installed(self, pattern: Optional[str] = None) -> bool:
        argv = self.cmd_list()
        if not pattern:
            return run(argv).ok
        res = run(argv, capture=True)
        if not res.ok:
            ui.fail(t("cmd_failed", res.returncode))
            return False
        needle = pattern.lower()
        found = [ln for ln in res.stdout.splitlines() if needle in ln.lower()]
        if found:
            print("\n".join(found))
        else:
            ui.info(t("no_matches"))
        return True

    # --- структурированные данные (используются TUI) ---
    def cmd_search_plain(self, query: str) -> List[str]:
        return self.cmd_search(query)

    def parse_search(self, output: str) -> List[PackageHit]:
        raise NotImplementedError

    def cmd_installed(self) -> List[str]:
        raise NotImplementedError

    def parse_installed(self, output: str) -> Dict[str, str]:
        raise NotImplementedError

    def search_hits(self, query: str) -> List[PackageHit]:
        """Поиск с разбором вывода. Код возврата не проверяем: pacman и dnf
        возвращают 1, если ничего не найдено."""
        res = run(self.cmd_search_plain(query), capture=True)
        seen, hits = set(), []
        for hit in self.parse_search(res.stdout):
            if hit.name not in seen:
                seen.add(hit.name)
                hits.append(hit)
        return hits

    def installed_packages(self) -> Dict[str, str]:
        res = run(self.cmd_installed(), capture=True)
        return self.parse_installed(res.stdout) if res.ok else {}

    def info_text(self, pkg: str) -> str:
        res = run(self.cmd_info(pkg), capture=True)
        return (res.stdout or res.stderr).strip()
