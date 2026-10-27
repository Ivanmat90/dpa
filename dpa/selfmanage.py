"""Установка автодополнения и удаление самого dpa."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

from . import completions, config, ui
from .i18n import t
from .options import OPTS
from .runtime import run

MARKER = "# dpa-completion"
BIN_PATH = Path("/usr/local/bin/dpa")
_LEGACY = ("bash_completion_dpa", "zsh_completion_dpa")


def _completion_files():
    cdir = config.config_dir()
    home = config.user_home()
    return {
        "bash": (cdir / "completion.bash", home / ".bashrc"),
        "zsh": (cdir / "completion.zsh", home / ".zshrc"),
        "fish": (home / ".config" / "fish" / "completions" / "dpa.fish", None),
    }


def _shell_present(shell: str) -> bool:
    home = config.user_home()
    if shell == "bash":
        return (home / ".bashrc").exists() or "bash" in os.environ.get("SHELL", "")
    if shell == "zsh":
        return (home / ".zshrc").exists() or "zsh" in os.environ.get("SHELL", "")
    return shutil.which("fish") is not None or (home / ".config" / "fish").exists()


def _add_rc_line(rc: Path, script: Path) -> None:
    line = '[ -f "%s" ] && . "%s"  %s' % (script, script, MARKER)
    text = rc.read_text(encoding="utf-8") if rc.exists() else ""
    if MARKER in text:
        return
    if text and not text.endswith("\n"):
        text += "\n"
    rc.write_text(text + line + "\n", encoding="utf-8")
    config.fix_owner(rc)


def install_completions(parser, only=None) -> List[str]:
    done = []
    for shell, (path, rc) in _completion_files().items():
        if only and shell not in only:
            continue
        if not only and not _shell_present(shell):
            continue
        try:
            config.ensure_dir(path.parent)
            path.write_text(completions.GENERATORS[shell](parser), encoding="utf-8")
            config.fix_owner(path)
            if rc is not None:
                _add_rc_line(rc, path)
            done.append(shell)
        except OSError as exc:
            ui.warn(t("uninstall_warn", path, exc))
    return done


def refresh_completions(parser) -> None:
    existing = [s for s, (p, _) in _completion_files().items() if p.exists()]
    if existing:
        install_completions(parser, only=existing)


def _strip_rc(rc: Path) -> None:
    if not rc.exists():
        return
    try:
        lines = rc.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [ln for ln in lines
                if MARKER not in ln and not any(k in ln for k in _LEGACY)]
        if len(kept) != len(lines):
            rc.write_text("".join(kept), encoding="utf-8")
    except OSError as exc:
        ui.warn(t("uninstall_warn", rc, exc))


def uninstall(keep_data: bool = False) -> bool:
    ui.section(t("uninstalling"))
    if not ui.confirm(t("uninstall_confirm"), default=False):
        ui.info(t("cancelled"))
        return False
    home = config.user_home()
    files = [home / ".bash_completion_dpa", home / ".zsh_completion_dpa"]
    files += [p for p, _ in _completion_files().values()]
    dirs = [config.cache_dir(), config.state_dir()]
    if not keep_data:
        dirs += [config.data_dir(), config.config_dir()]
    else:
        files = [f for f in files if config.config_dir() not in f.parents]
    for path in files:
        if path.is_file() and not OPTS.dry_run:
            try:
                path.unlink()
                ui.line(t("uninstall_removed", path))
            except OSError as exc:
                ui.warn(t("uninstall_warn", path, exc))
    for path in dirs:
        if path.is_dir() and not OPTS.dry_run:
            shutil.rmtree(path, ignore_errors=True)
            ui.line(t("uninstall_dir", path))
    for rc in (home / ".bashrc", home / ".zshrc"):
        if not OPTS.dry_run:
            _strip_rc(rc)
    if BIN_PATH.exists():
        res = run(["rm", "-f", str(BIN_PATH)], privileged=True)
        if res.ok and not OPTS.dry_run:
            ui.line(t("uninstall_removed", BIN_PATH))
        elif not res.ok:
            return False
    if OPTS.dry_run:
        return True
    ui.ok(t("uninstalled"))
    return True
