"""Необязательная зависимость TUI - библиотека Textual.

Ставится в приватное виртуальное окружение (~/.local/share/dpa/tui-venv):
не нужен root, системный Python не затрагивается, а CLI работает и без неё.
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import shutil
import site
import sys
from pathlib import Path
from typing import Optional

from .. import config, ui
from ..i18n import t
from ..options import OPTS
from ..runtime import run

REQUIREMENT = "textual>=1.0,<7"


def venv_dir() -> Path:
    return config.data_dir() / "tui-venv"


def venv_site_packages() -> Optional[Path]:
    ver = "python%d.%d" % sys.version_info[:2]
    path = venv_dir() / "lib" / ver / "site-packages"
    return path if path.is_dir() else None


def textual_available() -> bool:
    return importlib.util.find_spec("textual") is not None


def activate() -> bool:
    """Textual доступен в системе или в приватном venv?"""
    if textual_available():
        return True
    sp = venv_site_packages()
    if sp is not None:
        site.addsitedir(str(sp))
        importlib.invalidate_caches()
    return textual_available()


def _chown_tree(path: Path) -> None:
    if config.real_user() is None:
        return
    for root, dirs, files in os.walk(path):
        config.fix_owner(Path(root))
        for name in files:
            config.fix_owner(Path(root, name))


def install(backend_name: str = "") -> bool:
    """Создать venv и поставить Textual."""
    target = venv_dir()
    ui.info(t("tui_installing", str(target)))
    if target.exists() and not OPTS.dry_run:
        shutil.rmtree(target, ignore_errors=True)
    if not OPTS.dry_run:
        config.ensure_dir(target.parent)
    res = run([sys.executable, "-m", "venv", str(target)], mutating=True)
    if not res.ok:
        ui.fail(t("tui_venv_hint_apt" if backend_name == "apt" else "tui_venv_hint"))
        shutil.rmtree(target, ignore_errors=True)
        return False
    pip = [str(target / "bin" / "python"), "-m", "pip", "install",
           "--disable-pip-version-check", REQUIREMENT]
    if not run(pip, mutating=True).ok:
        ui.fail(t("tui_install_fail"))
        shutil.rmtree(target, ignore_errors=True)
        return False
    if not OPTS.dry_run:
        _chown_tree(target)
    if not OPTS.dry_run:
        ui.ok(t("tui_installed"))
    return True
