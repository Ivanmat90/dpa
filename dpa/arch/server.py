"""dpa arch-server: серверные пакеты, инициализация БД, автозапуск сервисов."""
from __future__ import annotations

from typing import List, Optional

from .. import ui
from ..i18n import t
from . import common

CATEGORIES = {
    "web": ["nginx"],
    "apache": ["apache"],
    "database": ["mariadb", "postgresql", "redis"],
    "devops": ["docker", "ansible", "terraform", "kubectl", "helm"],
    "monitoring": ["prometheus", "grafana"],
    "ci_cd": ["jenkins", "gitlab-runner"],
    "message": ["rabbitmq"],
}
DEFAULT = ["web", "database", "devops"]
SERVICE_OF = {"nginx": "nginx", "apache": "httpd", "mariadb": "mariadb",
              "postgresql": "postgresql", "redis": "redis", "docker": "docker",
              "prometheus": "prometheus", "grafana": "grafana",
              "jenkins": "jenkins", "gitlab-runner": "gitlab-runner",
              "rabbitmq": "rabbitmq"}


def parse_selection(raw: List[str]) -> List[str]:
    """Принимает имена категорий или их номера."""
    names = list(CATEGORIES)
    out = []
    for item in raw:
        if item.isdigit() and 1 <= int(item) <= len(names):
            out.append(names[int(item) - 1])
        else:
            out.append(item)
    return out


def run_arch_server(backend: str, target: str,
                    selected: Optional[List[str]] = None) -> bool:
    ui.section(t("arch_server_title"))
    if not common.preflight(backend, target, "arch-server"):
        return False
    if not selected:
        ui.info(t("arch_server_available"))
        ui.table(["#", t("col_category"), t("col_packages")],
                 [(str(i), k, ", ".join(v))
                  for i, (k, v) in enumerate(CATEGORIES.items(), 1)])
        ui.line()
        ui.line("  " + t("arch_server_enter"))
        ui.line("  " + t("arch_server_default"))
        raw = ui.prompt(">").split()
        selected = raw or DEFAULT
    packages: List[str] = []
    for svc in parse_selection(selected):
        if svc in CATEGORIES:
            packages.extend(CATEGORIES[svc])
        else:
            ui.warn(t("arch_server_unknown", svc))
    packages = list(dict.fromkeys(packages))
    if not packages:
        ui.fail(t("arch_server_none"))
        return False
    ui.info(t("arch_server_install", " ".join(packages)))
    if not common.pacman_in_target(target, packages):
        return False

    if "mariadb" in packages and not common.target_path(
            target, "/var/lib/mysql/mysql").exists():
        common.chroot_run(target, ["mariadb-install-db", "--user=mysql",
                                   "--basedir=/usr", "--datadir=/var/lib/mysql"])
    if "postgresql" in packages and not common.target_path(
            target, "/var/lib/postgres/data/PG_VERSION").exists():
        common.chroot_run(target, [
            "su", "-l", "postgres", "-c",
            "initdb --locale=C.UTF-8 --encoding=UTF8 -D /var/lib/postgres/data"])

    services = [SERVICE_OF[p] for p in packages if p in SERVICE_OF]
    if "nginx" in packages and "apache" in packages:
        ui.warn(t("arch_server_web_conflict"))
        services.remove("httpd")
    common.enable_services(target, services)

    ui.ok(t("arch_server_ok"))
    ui.info(t("arch_server_complete"))
    if not common.is_host_root(target):
        ui.line("  sudo dpa arch-config")
    return True
