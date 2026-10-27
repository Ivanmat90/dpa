from __future__ import annotations

from .base import Backend


def _y(yes):
    return ["-y"] if yes else []


class AptBackend(Backend):
    name = "apt"

    def cmd_install(self, pkgs, yes):
        return ["apt", "install"] + _y(yes) + list(pkgs)

    def cmd_remove(self, pkgs, yes):
        return ["apt", "remove"] + _y(yes) + list(pkgs)

    def cmd_refresh(self):
        return ["apt", "update"]

    def cmd_upgrade(self, yes):
        return ["apt", "upgrade"] + _y(yes)

    def cmd_search(self, query):
        return ["apt", "search", query]

    def cmd_info(self, pkg):
        return ["apt", "show", pkg]

    def cmd_list(self):
        return ["apt", "list", "--installed"]

    def cmd_clean(self, yes):
        return ["apt", "clean"]

    def cmd_autoremove(self, yes):
        return ["apt", "autoremove"] + _y(yes)

    def upgrade(self, yes=False):
        # на apt список пакетов нужно обновить перед upgrade
        return self.refresh() and super().upgrade(yes)
