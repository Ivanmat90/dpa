"""Выбор бэкенда по /etc/os-release и доступным бинарникам."""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Dict, Optional

from ..runtime import which
from .apt import AptBackend
from .base import Backend
from .dnf import DnfBackend
from .pacman import PacmanBackend

BACKENDS = {"apt": AptBackend, "dnf": DnfBackend, "pacman": PacmanBackend}

_FAMILY = (
    ({"debian", "ubuntu"}, "apt"),
    ({"fedora", "rhel", "centos"}, "dnf"),
    ({"arch"}, "pacman"),
)


@dataclass
class Distro:
    name: str = "Unknown"
    version: str = ""
    id: str = ""
    like: str = ""


def parse_os_release(path: str = "/etc/os-release") -> Dict[str, str]:
    data: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if "=" in raw and not raw.startswith("#"):
                    key, value = raw.split("=", 1)
                    data[key] = value.strip().strip('"').strip("'")
    except OSError:
        pass
    return data


def distro_info(path: str = "/etc/os-release") -> Distro:
    d = parse_os_release(path)
    return Distro(d.get("PRETTY_NAME") or d.get("NAME") or "Unknown",
                  d.get("VERSION_ID", ""), d.get("ID", ""), d.get("ID_LIKE", ""))


def detect_name(path: str = "/etc/os-release") -> Optional[str]:
    forced = os.environ.get("DPA_BACKEND", "").strip().lower()
    if forced in BACKENDS:
        return forced
    info = distro_info(path)
    tokens = {info.id.lower()} | set(info.like.lower().split())
    for family, pm in _FAMILY:
        if tokens & family and which(pm if pm != "pacman" else "pacman"):
            return pm
    for pm in ("dnf", "apt", "pacman"):
        if which(pm):
            return pm
    return None


def detect() -> Optional[Backend]:
    name = detect_name()
    return BACKENDS[name]() if name else None


def kernel() -> str:
    return "%s %s" % (platform.system(), platform.release())
