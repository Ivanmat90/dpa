"""dpa arch-dev: окружение разработчика (+ yay для указанного пользователя)."""
from __future__ import annotations

from typing import Optional

from .. import ui
from ..i18n import t
from . import common

DEV_PACKAGES = [
    "base-devel", "python", "python-pip", "nodejs", "npm", "go", "rust",
    "gcc", "git", "vim", "neovim", "emacs", "docker", "docker-compose",
    "kubectl", "helm", "terraform", "ansible", "htop", "tree", "tmux",
    "fastfetch", "fzf", "ripgrep", "bat", "eza", "zsh", "fish",
]

_YAY_BUILD = ("cd /tmp && rm -rf yay && git clone https://aur.archlinux.org/yay.git "
              "&& cd yay && makepkg --noconfirm")


def install_yay(target: str, user: str) -> bool:
    """makepkg нельзя запускать от root, поэтому собираем от имени user."""
    ui.info(t("arch_dev_aur"))
    if not common.chroot_run(target, ["runuser", "-u", user, "--", "bash", "-c",
                                      _YAY_BUILD]).ok:
        return False
    return common.chroot_run(target, ["bash", "-c",
                                      "pacman -U --noconfirm /tmp/yay/yay-*.pkg.tar.*"]).ok


def run_arch_dev(backend: str, target: str, user: Optional[str] = None) -> bool:
    ui.section(t("arch_dev_title"))
    if not common.preflight(backend, target, "arch-dev"):
        return False
    ui.info(t("arch_dev_install"))
    if not common.pacman_in_target(target, DEV_PACKAGES):
        return False
    common.enable_services(target, ["docker"])
    if user:
        if common.user_exists(target, user):
            common.add_user_to_groups(target, user, ["docker"])
            install_yay(target, user)
        else:
            ui.warn(t("arch_user_missing", user))
    else:
        ui.info(t("arch_dev_no_user"))
    ui.ok(t("arch_dev_ok"))
    ui.info(t("arch_dev_extra"))
    if not common.is_host_root(target):
        ui.line("  sudo dpa arch-config")
    return True
