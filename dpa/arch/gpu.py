"""Определение видеокарты и установка драйверов в целевую систему."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from .. import ui
from ..i18n import t
from ..runtime import run, write_file
from . import common

_MODERN_NVIDIA = re.compile(
    r"RTX|GTX\s*16\d\d|\b(TU1\d\d|GA1\d\d|AD1\d\d|GB[12]\d\d)\b", re.I)

PACKAGES = {
    "amd": ["mesa", "lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon"],
    "intel": ["mesa", "lib32-mesa", "vulkan-intel", "lib32-vulkan-intel"],
    "vmware": ["mesa", "xf86-video-vmware", "open-vm-tools"],
    "virtualbox": ["virtualbox-guest-utils"],
    "virtio": ["mesa"],
}
NVIDIA_MODERN = ["nvidia-open", "nvidia-utils", "lib32-nvidia-utils",
                 "nvidia-settings"]
NVIDIA_FALLBACK = ["mesa", "lib32-mesa"]


@dataclass
class Gpu:
    vendor: str
    model: str
    packages: List[str] = field(default_factory=list)
    legacy_nvidia: bool = False


def _vendor(low: str):
    if "nvidia" in low:
        return "nvidia"
    if "virtualbox" in low:
        return "virtualbox"
    if "vmware" in low:
        return "vmware"
    if "virtio" in low or "red hat" in low:
        return "virtio"
    if "amd" in low or "radeon" in low or "advanced micro" in low:
        return "amd"
    if "intel" in low:
        return "intel"
    return None


def parse_lspci(output: str) -> List[Gpu]:
    gpus: List[Gpu] = []
    for line in output.splitlines():
        if not re.search(r"VGA|3D controller|Display controller", line):
            continue
        vendor = _vendor(line.lower())
        if not vendor:
            continue
        if vendor == "nvidia":
            modern = bool(_MODERN_NVIDIA.search(line))
            gpus.append(Gpu(vendor, line.strip(),
                            list(NVIDIA_MODERN if modern else NVIDIA_FALLBACK),
                            legacy_nvidia=not modern))
        else:
            gpus.append(Gpu(vendor, line.strip(), list(PACKAGES[vendor])))
    return gpus


def detect() -> List[Gpu]:
    res = run(["lspci", "-nn"], capture=True)
    return parse_lspci(res.stdout) if res.ok else []


def _mkinit_modules(text: str) -> str:
    mods = "nvidia nvidia_modeset nvidia_uvm nvidia_drm"
    def repl(m):
        existing = m.group(1).split()
        extra = [x for x in mods.split() if x not in existing]
        return "MODULES=(%s)" % " ".join(existing + extra)
    new, n = re.subn(r"^MODULES=\(([^)]*)\)", repl, text, count=1, flags=re.M)
    return new if n else text + "\nMODULES=(%s)\n" % mods


def configure_nvidia(target: str) -> None:
    write_file(common.target_path(target, "/etc/modprobe.d/nvidia.conf"),
               "options nvidia_drm modeset=1\n")
    ui.ok(t("gpu_nvidia_config"))
    conf = common.target_path(target, "/etc/mkinitcpio.conf")
    try:
        text = conf.read_text(encoding="utf-8")
    except OSError:
        return
    if "nvidia" not in text:
        if write_file(conf, _mkinit_modules(text)):
            ui.ok(t("gpu_nvidia_mkinit"))
            common.chroot_run(target, ["mkinitcpio", "-P"])


def install_drivers(target: str) -> bool:
    ui.info(t("gpu_detecting"))
    gpus = detect()
    if not gpus:
        ui.warn(t("gpu_unknown"))
        return True
    pkgs: List[str] = []
    for gpu in gpus:
        ui.line(t("gpu_detected", gpu.model))
        ui.line(t("gpu_vendor", gpu.vendor.upper()))
        if gpu.legacy_nvidia:
            ui.warn(t("gpu_nvidia_legacy"))
        pkgs.extend(gpu.packages)
    pkgs = list(dict.fromkeys(pkgs))
    if any(p.startswith("lib32-") for p in pkgs):
        common.enable_multilib(target)
    if not common.pacman_in_target(target, pkgs):
        ui.fail(t("gpu_failed", ", ".join(g.vendor for g in gpus)))
        return False
    if any(g.vendor == "nvidia" and not g.legacy_nvidia for g in gpus):
        configure_nvidia(target)
    if any(g.vendor == "virtualbox" for g in gpus):
        common.enable_services(target, ["vboxservice"])
    ui.ok(t("gpu_ok", ", ".join(g.vendor.upper() for g in gpus)))
    return True
