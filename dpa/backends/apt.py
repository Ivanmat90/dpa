from __future__ import annotations

from typing import Dict, List

from .base import Backend, PackageHit


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

    def cmd_search_plain(self, query):
        return ["apt-cache", "search", query]

    def parse_search(self, output):
        hits: List[PackageHit] = []
        for line in output.splitlines():
            name, sep, desc = line.partition(" - ")
            if sep and name and " " not in name.strip():
                hits.append(PackageHit(name.strip(), "", desc.strip()))
        return hits

    def cmd_installed(self):
        return ["dpkg-query", "-W", "-f=${db:Status-Abbrev}\\t${Package}\\t${Version}\\n"]

    def parse_installed(self, output) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for line in output.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0].strip().startswith("ii"):
                result[parts[1]] = parts[2]
        return result
