"""Общие помощники для установки Arch Linux в целевую систему (/mnt)."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from .. import ui
from ..i18n import t
from ..options import OPTS
from ..runtime import Result, is_root, run, which, write_file


def is_host_root(target: str) -> bool:
    return str(target) in ("/", "")


def auto_target() -> str:
    """Куда ставить, если --target не указан.

    Live-ISO: всегда /mnt (иначе пакеты ушли бы в ОЗУ live-системы).
    Установленная система: /mnt, только если там что-то смонтировано, иначе
    сама работающая система (/).
    """
    if os.path.ismount("/mnt") or os.path.isdir("/run/archiso"):
        return "/mnt"
    return "/"


def preflight(backend_name: str, target: str, command: str, *,
              need_base: bool = True, need_mount: bool = True) -> bool:
    """Проверки перед установкой. В --dry-run проблемы только предупреждают."""
    problems: List[str] = []
    if backend_name != "pacman" and not os.path.exists("/etc/arch-release"):
        problems.append(t("error_not_arch"))
    if not is_root():
        problems.append(t("error_root", command))
    host = is_host_root(target)
    tools = ["pacman"] if host else ["pacstrap", "arch-chroot"]
    missing = [x for x in tools if not which(x)]
    if missing:
        problems.append(t("error_tools", ", ".join(missing)))
    if need_mount and not host and not os.path.ismount(target):
        problems.append(t("error_mount", target))
        problems.append(t("error_mount_help", target))
    if need_base and not host and not Path(target, "usr/bin/pacman").exists():
        problems.append(t("error_no_base", target))
    for msg in problems:
        (ui.warn if OPTS.dry_run else ui.fail)(msg)
    if OPTS.dry_run or not problems:
        ui.line(t("arch_target", t("arch_target_running") if host else target))
    return OPTS.dry_run or not problems


def chroot_run(target: str, argv: Sequence[str], *, show: bool = True) -> Result:
    cmd = list(argv) if is_host_root(target) else ["arch-chroot", str(target)] + list(argv)
    return run(cmd, mutating=True, show=show)


def target_path(target: str, rel: str) -> Path:
    return Path(target) / rel.lstrip("/")


def pacman_in_target(target: str, packages: Iterable[str]) -> bool:
    pkgs = list(dict.fromkeys(packages))
    if not pkgs:
        return True
    return chroot_run(target, ["pacman", "-Syu", "--needed", "--noconfirm"] + pkgs).ok


def enable_multilib_text(text: str) -> Tuple[str, bool]:
    """Раскомментировать секцию [multilib] в pacman.conf."""
    out, changed, in_section = [], False, False
    for raw in text.splitlines():
        s = raw.strip()
        if re.fullmatch(r"#?\s*\[multilib\]", s):
            in_section = True
            if s.startswith("#"):
                changed = True
            out.append("[multilib]")
            continue
        if in_section:
            if re.fullmatch(r"#\s*Include\s*=.*", s):
                raw = re.sub(r"^\s*#\s*", "", raw)
                changed = True
                in_section = False
            elif s.startswith("Include") or s.startswith("["):
                in_section = False
        out.append(raw)
    return "\n".join(out) + "\n", changed


def enable_multilib(target: str) -> bool:
    conf = target_path(target, "/etc/pacman.conf")
    try:
        text = conf.read_text(encoding="utf-8")
    except OSError as exc:
        if OPTS.dry_run:
            ui.dry(t("arch_multilib"))
            return True
        ui.fail(t("write_failed", str(conf), exc))
        return False
    new, changed = enable_multilib_text(text)
    if changed:
        ui.info(t("arch_multilib"))
        return write_file(conf, new)
    return True


def enable_services(target: str, services: Iterable[str]) -> None:
    for svc in services:
        if chroot_run(target, ["systemctl", "enable", svc], show=False).ok:
            ui.ok(t("arch_service_enabled", svc))


def existing_groups(target: str, wanted: Iterable[str]) -> List[str]:
    try:
        text = target_path(target, "/etc/group").read_text(encoding="utf-8")
    except OSError:
        return list(wanted) if OPTS.dry_run else []
    have = {ln.split(":", 1)[0] for ln in text.splitlines() if ":" in ln}
    return [g for g in wanted if g in have]


def user_exists(target: str, user: str) -> bool:
    try:
        text = target_path(target, "/etc/passwd").read_text(encoding="utf-8")
    except OSError:
        return False
    return any(ln.split(":", 1)[0] == user for ln in text.splitlines())


def add_user_to_groups(target: str, user: str, groups: Iterable[str]) -> None:
    present = existing_groups(target, groups)
    if present:
        chroot_run(target, ["usermod", "-aG", ",".join(present), user], show=False)
