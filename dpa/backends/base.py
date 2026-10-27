"""Общий интерфейс бэкендов. Каждый бэкенд только описывает команды."""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from .. import ui
from ..i18n import t
from ..runtime import run


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
