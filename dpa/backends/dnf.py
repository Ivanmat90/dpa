from __future__ import annotations

from .base import Backend


def _y(yes):
    return ["-y"] if yes else []


class DnfBackend(Backend):
    name = "dnf"
    refresh_ok_codes = (0, 100)  # 100 = есть доступные обновления

    def cmd_install(self, pkgs, yes):
        return ["dnf", "install"] + _y(yes) + list(pkgs)

    def cmd_remove(self, pkgs, yes):
        return ["dnf", "remove"] + _y(yes) + list(pkgs)

    def cmd_refresh(self):
        return ["dnf", "check-update", "--refresh"]

    def cmd_upgrade(self, yes):
        return ["dnf", "upgrade"] + _y(yes)

    def cmd_search(self, query):
        return ["dnf", "search", query]

    def cmd_info(self, pkg):
        return ["dnf", "info", pkg]

    def cmd_list(self):
        return ["dnf", "list", "--installed"]

    def cmd_clean(self, yes):
        return ["dnf", "clean", "all"]

    def cmd_autoremove(self, yes):
        return ["dnf", "autoremove"] + _y(yes)
