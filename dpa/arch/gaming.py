"""dpa arch-gaming: Steam, Wine, Lutris и т.д. (нужен multilib)."""
from __future__ import annotations

from typing import Optional

from .. import ui
from ..i18n import t
from . import common, gpu

GAMING_PACKAGES = ["steam", "lutris", "wine", "winetricks", "gamemode",
                   "mangohud", "goverlay", "discord", "obs-studio", "ffmpeg"]
SUMMARY = ["Steam", "Lutris", "Wine", "Gamemode", "MangoHud", "OBS Studio",
           "Discord"]


def run_arch_gaming(backend: str, target: str, user: Optional[str] = None,
                    with_gpu: bool = True) -> bool:
    ui.section(t("arch_gaming_title"))
    if not common.preflight(backend, target, "arch-gaming"):
        return False
    common.enable_multilib(target)  # steam и lib32-* есть только в multilib
    ui.info(t("arch_gaming_install"))
    if not common.pacman_in_target(target, GAMING_PACKAGES):
        return False
    if with_gpu:
        gpu.install_drivers(target)  # Vulkan-драйверы нужны Steam/Wine
    if user:
        if common.user_exists(target, user):
            common.add_user_to_groups(target, user, ["gamemode", "audio", "video"])
        else:
            ui.warn(t("arch_user_missing", user))
    ui.ok(t("arch_gaming_ok"))
    ui.line(t("arch_gaming_list"))
    ui.bullets(SUMMARY)
    return True
