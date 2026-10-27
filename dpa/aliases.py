"""Единые имена пакетов для разных дистрибутивов.

В BUILTIN указываются только отличия: если для менеджера записи нет,
пакет называется так же, как канонический ключ.
Значение может быть строкой или списком пакетов.
"""
from __future__ import annotations

import re
from typing import Dict, List, Sequence, Union

from . import ui
from .db import Database
from .i18n import t

BUILTIN: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "build-essential": {"dnf": ["gcc", "gcc-c++", "make"], "pacman": "base-devel"},
    "python": {"apt": "python3", "dnf": "python3"},
    "python-pip": {"apt": "python3-pip", "dnf": "python3-pip"},
    "python-dev": {"apt": "python3-dev", "dnf": "python3-devel", "pacman": "python"},
    "libssl-dev": {"dnf": "openssl-devel", "pacman": "openssl"},
    "openssh-server": {"pacman": "openssh"},
    "dnsutils": {"dnf": "bind-utils", "pacman": "bind"},
    "fd": {"apt": "fd-find", "dnf": "fd-find"},
    "mysql": {"apt": "mysql-server", "dnf": "mariadb-server", "pacman": "mariadb"},
    "postgresql": {"dnf": "postgresql-server"},
    "apache": {"apt": "apache2", "dnf": "httpd"},
    "redis": {"apt": "redis-server"},
    "docker": {"apt": "docker.io", "dnf": "moby-engine"},
    "golang": {"pacman": "go"},
    "imagemagick": {"dnf": "ImageMagick"},
    "gnome": {"apt": "gnome-shell", "dnf": "gnome-shell"},
    "kde": {"apt": "plasma-desktop", "dnf": "plasma-desktop", "pacman": "plasma"},
    "xfce": {"apt": "xfce4", "dnf": "@xfce-desktop-environment", "pacman": "xfce4"},
}

_NAME_RE = re.compile(r"^[A-Za-z0-9@][A-Za-z0-9@._+:/~-]*$")


def valid_name(name: str) -> bool:
    return bool(_NAME_RE.match(name))


def builtin_for(name: str, pm: str) -> List[str]:
    entry = BUILTIN.get(name, {}).get(pm)
    if entry is None:
        return []
    return [entry] if isinstance(entry, str) else list(entry)


def resolve(names: Sequence[str], pm: str, db: Database,
            announce: bool = True) -> List[str]:
    """Пользовательский алиас -> встроенный -> имя как есть."""
    result: List[str] = []
    for name in names:
        custom = db.get_alias(name, pm)
        if custom:
            targets, kind = custom.split(), "alias_custom_resolved"
        else:
            targets, kind = builtin_for(name, pm), "alias_resolved"
        if targets and targets != [name]:
            if announce:
                ui.info(t(kind, name, " ".join(targets), pm.upper()))
            result.extend(targets)
        else:
            result.append(name)
    return result
