from __future__ import annotations

import re
from typing import Dict, List

from .base import Backend, PackageHit

_DNF_LINE = re.compile(
    r"^\s*([A-Za-z0-9_.+@-]+?)\.(x86_64|noarch|i686|aarch64|armv7hl|ppc64le|s390x|src)"
    r"\s*(?::\s*|\s{2,})(.*)$")


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

    def cmd_search_plain(self, query):
        return ["dnf", "search", "-q", query]

    def parse_search(self, output):
        hits: List[PackageHit] = []
        for line in output.splitlines():
            m = _DNF_LINE.match(line)
            if m:
                hits.append(PackageHit(m.group(1), "", m.group(3).strip()))
        return hits

    def cmd_installed(self):
        return ["rpm", "-qa", "--qf", "%{NAME}\\t%{VERSION}-%{RELEASE}\\n"]

    def parse_installed(self, output) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for line in output.splitlines():
            name, _, ver = line.partition("\t")
            if name:
                result[name] = ver
        return result
