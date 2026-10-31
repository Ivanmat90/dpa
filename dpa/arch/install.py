"""dpa arch-install: базовая система через pacstrap."""
from __future__ import annotations

import re
from typing import List, Optional

from .. import ui
from ..i18n import t
from ..options import OPTS
from ..runtime import run, write_file
from . import common

BASE_PACKAGES = ["base", "linux", "linux-firmware", "vim", "sudo",
                 "networkmanager", "grub", "efibootmgr"]


def cpu_microcode() -> Optional[str]:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    if "GenuineIntel" in text:
        return "intel-ucode"
    if "AuthenticAMD" in text:
        return "amd-ucode"
    return None


def run_arch_install(backend: str, target: str, extra: Optional[List[str]]) -> bool:
    ui.section(t("arch_install_title"))
    if common.is_host_root(target):
        ui.fail(t("arch_install_host_root"))
        return False
    if not common.preflight(backend, target, "arch-install", need_base=False):
        return False
    packages = list(BASE_PACKAGES)
    ucode = cpu_microcode()
    if ucode:
        packages.append(ucode)
    packages += extra or []
    packages = list(dict.fromkeys(packages))

    ui.info(t("arch_install_base"))
    if not run(["pacstrap", "-K", target] + packages, mutating=True).ok:
        return False

    ui.info(t("arch_install_fstab"))
    if OPTS.dry_run:
        ui.dry("genfstab -U %s > %s/etc/fstab" % (target, target))
    else:
        res = run(["genfstab", "-U", target], capture=True)
        if not res.ok or not res.stdout.strip():
            ui.fail(t("arch_install_fstab_fail"))
            return False
        write_file(common.target_path(target, "/etc/fstab"), res.stdout)

    ui.info(t("arch_install_config"))
    common.enable_services(target, ["NetworkManager"])

    ui.ok(t("arch_install_ok"))
    ui.line(t("arch_install_path", target))
    ui.line()
    ui.info(t("arch_install_next"))
    ui.line(t("arch_install_step1", target))
    ui.line(t("arch_install_step2"))
    ui.line(t("arch_install_step3"))
    return True
