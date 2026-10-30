from __future__ import annotations

import re
from typing import Dict, List

from .. import ui
from ..i18n import t
from ..runtime import run, which
from .base import Backend, PackageHit

_HEAD = re.compile(r"^(?P<repo>[^\s/]+)/(?P<name>\S+)\s+(?P<ver>\S+)(?P<rest>.*)$")


def _nc(yes):
    return ["--noconfirm"] if yes else []


class PacmanBackend(Backend):
    name = "pacman"

    def cmd_install(self, pkgs, yes):
        return ["pacman", "-S", "--needed"] + _nc(yes) + list(pkgs)

    def cmd_remove(self, pkgs, yes):
        return ["pacman", "-Rs"] + _nc(yes) + list(pkgs)

    def cmd_refresh(self):
        return ["checkupdates"]

    def cmd_upgrade(self, yes):
        return ["pacman", "-Syu"] + _nc(yes)

    def cmd_search(self, query):
        return ["pacman", "-Ss", query]

    def cmd_info(self, pkg):
        return ["pacman", "-Si", pkg]

    def cmd_list(self):
        return ["pacman", "-Q"]

    def cmd_clean(self, yes):
        if which("paccache"):
            return ["paccache", "-r"]
        return ["pacman", "-Sc"] + _nc(yes)

    def cmd_autoremove(self, yes):
        raise NotImplementedError  # нужен список сирот, см. autoremove()

    def refresh(self):
        """На Arch нельзя делать `pacman -Sy` без апгрейда (частичное
        обновление ломает систему), поэтому только показываем обновления."""
        if which("checkupdates"):
            return run(["checkupdates"], ok_codes=(0, 2)).ok
        ui.warn(t("pacman_refresh_note"))
        return True

    def info(self, pkg):
        res = run(["pacman", "-Si", pkg], capture=True)
        if not res.ok:
            res = run(["pacman", "-Qi", pkg], capture=True)
        if res.ok:
            print(res.stdout, end="")
            return True
        ui.fail(t("pkg_not_found", pkg))
        return False

    def autoremove(self, yes=False):
        res = run(["pacman", "-Qdtq"], capture=True, ok_codes=(0, 1))
        if not res.ok:
            ui.fail(t("cmd_failed", res.returncode))
            return False
        orphans = res.stdout.split()
        if not orphans:
            ui.info(t("nothing_to_remove"))
            return True
        ui.info(t("orphans_found", ", ".join(orphans)))
        return self._exec("autoremove",
                          ["pacman", "-Rns"] + _nc(yes) + orphans)

    def cmd_search_plain(self, query):
        return ["pacman", "-Ss", query]

    def parse_search(self, output):
        hits: List[PackageHit] = []
        for line in output.splitlines():
            if line.startswith((" ", "\t")):
                if hits and not hits[-1].description:
                    hits[-1].description = line.strip()
                continue
            m = _HEAD.match(line)
            if m:
                hits.append(PackageHit(m.group("name"), m.group("ver"), "",
                                       "[installed" in m.group("rest")))
        return hits

    def cmd_installed(self):
        return ["pacman", "-Q"]

    def parse_installed(self, output) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for line in output.splitlines():
            name, _, ver = line.partition(" ")
            if name:
                result[name] = ver
        return result

    def info_text(self, pkg):
        res = run(["pacman", "-Si", pkg], capture=True)
        if not res.ok:
            res = run(["pacman", "-Qi", pkg], capture=True)
        return (res.stdout or res.stderr).strip()
