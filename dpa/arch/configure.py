"""dpa arch-config: локаль, часовой пояс, hostname, пароли, пользователь, GRUB.

Работает из live-ISO над смонтированной системой (--target /mnt) или внутри
chroot (--target /). Внутри chroot самого dpa нет, поэтому первый вариант
основной.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List

from .. import ui
from ..i18n import t
from ..options import OPTS
from ..runtime import run, write_file
from . import common


def default_target() -> str:
    return "/mnt" if os.path.ismount("/mnt") else "/"


def _enable_locales(text: str, locales: List[str]) -> str:
    for loc in locales:
        pat = re.compile(r"^#\s*(%s\s+UTF-8)\s*$" % re.escape(loc), re.M)
        if pat.search(text):
            text = pat.sub(r"\1", text)
        elif not re.search(r"^%s\s+UTF-8" % re.escape(loc), text, re.M):
            text += "\n%s UTF-8\n" % loc
    return text


def run_arch_config(backend: str, target: str) -> bool:
    ui.section(t("arch_config_title"))
    if not common.preflight(backend, target, "arch-config"):
        return False
    ui.line(t("arch_config_target", target))
    P = lambda rel: common.target_path(target, rel)
    cr = lambda argv, **kw: common.chroot_run(target, argv, **kw)

    # локаль
    ui.info(t("arch_config_locale"))
    answer = ui.prompt(t("arch_config_enter_locale"), "en_US.UTF-8")
    locales = [x for x in re.split(r"[\s,]+", answer) if x]
    try:
        text = P("/etc/locale.gen").read_text(encoding="utf-8")
    except OSError:
        text = ""
    write_file(P("/etc/locale.gen"), _enable_locales(text, locales))
    cr(["locale-gen"], show=False)
    write_file(P("/etc/locale.conf"), "LANG=%s\n" % locales[0])

    # часовой пояс и раскладка консоли
    tz = ui.prompt(t("arch_config_enter_tz"), "UTC")
    if P("/usr/share/zoneinfo/" + tz).exists() or OPTS.dry_run:
        cr(["ln", "-sf", "/usr/share/zoneinfo/" + tz, "/etc/localtime"], show=False)
        cr(["hwclock", "--systohc"], show=False)
    else:
        ui.warn(t("arch_config_bad_tz", tz))
    keymap = ui.prompt(t("arch_config_enter_keymap"), "us")
    write_file(P("/etc/vconsole.conf"), "KEYMAP=%s\n" % keymap)

    # hostname
    ui.info(t("arch_config_hostname"))
    host = ui.prompt(t("arch_config_enter_host"), "archlinux")
    write_file(P("/etc/hostname"), host + "\n")
    write_file(P("/etc/hosts"),
               "127.0.0.1\tlocalhost\n::1\t\tlocalhost\n"
               "127.0.1.1\t%s.localdomain\t%s\n" % (host, host))

    # root
    ui.info(t("arch_config_root_pw"))
    cr(["passwd"])

    # пользователь
    ui.info(t("arch_config_user"))
    if ui.confirm(t("arch_config_create"), default=False):
        user = ui.prompt(t("arch_config_username"))
        if user and re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", user):
            groups = common.existing_groups(
                target, ["wheel", "audio", "video", "storage", "network"])
            cr(["useradd", "-m", "-G", ",".join(groups), "-s", "/bin/bash", user])
            ui.line(t("arch_config_set_pw", user))
            cr(["passwd", user])
            sudo_file = P("/etc/sudoers.d/10-wheel")
            write_file(sudo_file, "%wheel ALL=(ALL:ALL) ALL\n", mode=0o440)
            if not OPTS.dry_run and not cr(["visudo", "-cf", "/etc/sudoers.d/10-wheel"],
                                           show=False).ok:
                sudo_file.unlink()
                ui.fail(t("arch_config_sudo_bad"))
            ui.ok(t("arch_config_user_ok", user))
        elif user:
            ui.fail(t("arch_config_bad_user", user))

    # загрузчик
    ui.info(t("arch_config_boot"))
    if not P("/usr/bin/grub-install").exists() and not OPTS.dry_run:
        ui.warn(t("arch_config_no_grub"))
    else:
        default_mode = "uefi" if os.path.isdir("/sys/firmware/efi") else "bios"
        mode = ui.prompt(t("arch_config_boot_mode"), default_mode).lower()
        if mode == "uefi":
            efi = "/boot/efi" if os.path.ismount(str(P("/boot/efi"))) else "/boot"
            cr(["grub-install", "--target=x86_64-efi", "--efi-directory=" + efi,
                "--bootloader-id=GRUB"])
        elif mode == "bios":
            disk = ui.prompt(t("arch_config_disk"))
            if disk:
                cr(["grub-install", "--target=i386-pc", disk])
        else:
            ui.warn(t("arch_config_skip"))
        if mode in ("uefi", "bios"):
            cr(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])

    ui.ok(t("arch_config_ok"))
    ui.info(t("arch_config_exit"))
    return True
