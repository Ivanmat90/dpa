"""dpa arch-desktop: графическое окружение + драйверы видеокарты."""
from __future__ import annotations

from .. import ui
from ..i18n import t
from . import common, gpu

DESKTOPS = {
    "gnome": {"packages": ["gnome", "gdm", "gnome-tweaks"], "service": "gdm",
              "desc": "GNOME Desktop Environment"},
    "kde": {"packages": ["plasma", "sddm", "konsole", "dolphin"],
            "service": "sddm", "desc": "KDE Plasma Desktop"},
    "xfce": {"packages": ["xfce4", "xfce4-goodies", "lightdm",
                          "lightdm-gtk-greeter"], "service": "lightdm",
             "desc": "XFCE Desktop Environment"},
    "cinnamon": {"packages": ["cinnamon", "lightdm", "lightdm-gtk-greeter"],
                 "service": "lightdm", "desc": "Cinnamon Desktop Environment"},
    "mate": {"packages": ["mate", "mate-extra", "lightdm",
                          "lightdm-gtk-greeter"], "service": "lightdm",
             "desc": "MATE Desktop Environment"},
    "lxqt": {"packages": ["lxqt", "sddm"], "service": "sddm",
             "desc": "LXQt Desktop Environment"},
    "i3": {"packages": ["i3-wm", "i3status", "i3lock", "dmenu", "alacritty",
                        "xorg-server", "xorg-xinit"], "service": None,
           "desc": "i3 Window Manager", "start": "startx /usr/bin/i3"},
    "sway": {"packages": ["sway", "waybar", "wofi", "foot", "swaylock"],
             "service": None, "desc": "Sway Wayland Compositor",
             "start": "sway"},
}


def run_arch_desktop(backend: str, de: str, target: str, with_gpu: bool = True) -> bool:
    env = DESKTOPS.get(de)
    if env is None:
        ui.fail(t("arch_desktop_not_found", de))
        ui.line(t("arch_desktop_available"))
        for key, item in DESKTOPS.items():
            ui.line("  %-10s %s" % (key, item["desc"]))
        ui.line(t("arch_desktop_example"))
        return False
    ui.section(t("arch_desktop_title", env["desc"]))
    if not common.preflight(backend, target, "arch-desktop"):
        return False
    ui.info(t("arch_desktop_packages", " ".join(env["packages"])))
    if not common.pacman_in_target(target, env["packages"]):
        return False
    if with_gpu:
        ui.line()
        ui.info(t("arch_desktop_gpu"))
        gpu.install_drivers(target)
    if env["service"]:
        common.enable_services(target, [env["service"]])
    ui.ok(t("arch_desktop_ok", env["desc"]))
    if env.get("start"):
        ui.info(t("arch_desktop_start", env["start"]))
    ui.info(t("arch_desktop_reboot"))
    if not common.is_host_root(target):
        ui.info(t("arch_need_config"))
    return True
