"""Пути, конфиг-файл и выбор языка.

Если dpa запущен через sudo, все файлы лежат в домашней директории
настоящего пользователя (SUDO_USER), а не root, и принадлежат ему.
"""
from __future__ import annotations

import json
import os
import pwd
from pathlib import Path
from typing import Dict, Optional

from . import __version__
from .i18n import SUPPORTED


def real_user() -> Optional[str]:
    if os.geteuid() == 0:
        user = os.environ.get("SUDO_USER")
        if user and user != "root":
            return user
    return None


def user_home() -> Path:
    user = real_user()
    if user:
        try:
            return Path(pwd.getpwnam(user).pw_dir)
        except KeyError:
            pass
    return Path.home()


def config_dir() -> Path:
    return user_home() / ".config" / "dpa"


def data_dir() -> Path:
    return user_home() / ".local" / "share" / "dpa"


def cache_dir() -> Path:
    return user_home() / ".cache" / "dpa"


def state_dir() -> Path:
    return user_home() / ".local" / "state" / "dpa"


def config_file() -> Path:
    return config_dir() / "config.json"


def fix_owner(path: Path) -> None:
    """Если работаем под sudo - отдаём файл настоящему пользователю."""
    user = real_user()
    if not user:
        return
    try:
        info = pwd.getpwnam(user)
        os.chown(path, info.pw_uid, info.pw_gid)
    except (KeyError, OSError):
        pass


def ensure_dir(path: Path) -> Path:
    missing = []
    cur = Path(path)
    while not cur.exists() and cur != cur.parent:
        missing.append(cur)
        cur = cur.parent
    Path(path).mkdir(parents=True, exist_ok=True)
    for item in missing:
        fix_owner(item)
    return Path(path)


def load_config() -> Dict:
    try:
        with open(config_file(), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_config(data: Dict) -> bool:
    try:
        ensure_dir(config_dir())
        data = dict(data)
        data["version"] = __version__
        with open(config_file(), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        fix_owner(config_file())
        return True
    except OSError:
        return False


def resolve_language() -> str:
    """DPA_LANG -> config.json -> локаль системы -> en."""
    env = os.environ.get("DPA_LANG", "").strip().lower()
    if env in SUPPORTED:
        return env
    saved = str(load_config().get("language", "")).lower()
    if saved in SUPPORTED:
        return saved
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "").lower()
        if value:
            return "ru" if value.startswith("ru") else "en"
    return "en"
