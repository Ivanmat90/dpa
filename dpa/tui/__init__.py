"""Необязательный текстовый интерфейс. Этот модуль не требует Textual:
библиотека подключается только внутри run_app()."""
from __future__ import annotations

import sys

from .. import ui
from ..i18n import t
from ..options import OPTS
from . import deps


def launch(backend, db, install_only: bool = False) -> bool:
    ui.section(t("tui_title"))
    if not deps.activate():
        ui.warn(t("tui_missing"))
        ui.line("  " + t("tui_install_info", str(deps.venv_dir())))
        ui.line()
        if not (install_only or ui.confirm(t("tui_install_ask"), default=False)):
            ui.info(t("tui_skipped"))
            return False
        if not deps.install(backend.name):
            return False
        if OPTS.dry_run:
            return True
        if not deps.activate():
            ui.fail(t("tui_install_fail"))
            return False
    if install_only:
        ui.ok(t("tui_deps_ready"))
        return True
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        ui.fail(t("tui_need_tty"))
        return False
    from .app import run_app  # здесь впервые импортируется Textual
    return run_app(backend, db)
