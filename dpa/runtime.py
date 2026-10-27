"""Запуск внешних команд: sudo, --dry-run, единый вывод ошибок."""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from . import ui
from .i18n import t
from .options import OPTS


@dataclass
class Result:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    ok: bool = True


def is_root() -> bool:
    return os.geteuid() == 0


def which(name: str) -> Optional[str]:
    return shutil.which(name)


def _with_privilege(argv):
    if is_root():
        return list(argv)
    for helper in ("sudo", "doas"):
        if which(helper):
            return [helper] + list(argv)
    return None


def run(argv: Sequence, *, privileged: bool = False, capture: bool = False,
        ok_codes: Sequence[int] = (0,), quiet: Optional[bool] = None,
        mutating: Optional[bool] = None, show: bool = True,
        input_text: Optional[str] = None, cwd=None, env=None) -> Result:
    """Выполнить команду.

    privileged - добавить sudo/doas, если мы не root;
    mutating   - команда меняет систему (в --dry-run не выполняется);
                 по умолчанию равно privileged;
    capture    - собрать вывод вместо печати (read-only запросы).
    """
    argv = [str(a) for a in argv]
    if quiet is None:
        quiet = capture
    if privileged:
        full = _with_privilege(argv)
        if full is None:
            ui.fail(t("error_no_sudo"))
            return Result(127, "", "", False)
        argv = full
    if mutating is None:
        mutating = privileged
    if mutating and OPTS.dry_run:
        ui.dry(" ".join(shlex.quote(a) for a in argv))
        return Result(0, "", "", True)
    if show and not quiet:
        ui.command_line(argv)
    try:
        proc = subprocess.run(argv, input=input_text, cwd=cwd, env=env,
                              text=True, capture_output=capture)
    except FileNotFoundError:
        if not quiet:
            ui.fail(t("cmd_not_found", argv[0]))
        return Result(127, "", "", False)
    ok = proc.returncode in tuple(ok_codes)
    if not ok and not quiet:
        ui.fail(t("cmd_failed", proc.returncode))
    return Result(proc.returncode, proc.stdout or "", proc.stderr or "", ok)


def write_file(path, content: str, mode: Optional[int] = None,
               append: bool = False) -> bool:
    path = Path(path)
    if OPTS.dry_run:
        ui.dry(t("dry_write", str(path)))
        return True
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a" if append else "w", encoding="utf-8") as fh:
            fh.write(content)
        if mode is not None:
            os.chmod(path, mode)
        return True
    except OSError as exc:
        ui.fail(t("write_failed", str(path), exc))
        return False
