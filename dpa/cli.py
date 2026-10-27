"""Командная строка DPA: разбор аргументов и диспетчеризация."""
from __future__ import annotations

import argparse
import platform
import sys
from typing import List, Optional

from . import __version__, completions, config, selfmanage, ui
from .arch.configure import default_target, run_arch_config
from .arch.desktop import DESKTOPS, run_arch_desktop
from .arch.dev import run_arch_dev
from .arch.gaming import run_arch_gaming
from .arch.install import run_arch_install
from .arch.server import CATEGORIES, run_arch_server
from .backends import detect, distro_info, kernel
from .db import Database
from .i18n import SUPPORTED, get_language, set_language, t
from .manager import PackageService
from .options import OPTS

# (группа, имя, псевдонимы, ключ справки, аргументы для обзора)
COMMANDS = [
    ("grp_packages", "install", ("i", "add"), "help_install", "<pkg>..."),
    ("grp_packages", "remove", ("rm",), "help_remove", "<pkg>..."),
    ("grp_packages", "update", (), "help_update", ""),
    ("grp_packages", "upgrade", ("up",), "help_upgrade", ""),
    ("grp_packages", "search", ("s",), "help_search", "<query>"),
    ("grp_packages", "info", ("show",), "help_info", "<pkg>"),
    ("grp_packages", "list", ("ls",), "help_list", "[filter]"),
    ("grp_packages", "clean", (), "help_clean", ""),
    ("grp_packages", "autoremove", (), "help_autoremove", ""),
    ("grp_tools", "history", ("log",), "help_history", "[-n N]"),
    ("grp_tools", "alias", (), "help_alias", "add|list|remove"),
    ("grp_tools", "distro", (), "help_distro", ""),
    ("grp_tools", "lang", (), "help_lang", "[en|ru]"),
    ("grp_tools", "completion", (), "help_completion", "bash|zsh|fish"),
    ("grp_tools", "uninstall", (), "help_uninstall", ""),
    ("grp_arch", "arch-install", (), "help_arch_install", "[--target DIR]"),
    ("grp_arch", "arch-config", (), "help_arch_config", "[--target DIR]"),
    ("grp_arch", "arch-desktop", (), "help_arch_desktop", "--de NAME"),
    ("grp_arch", "arch-server", (), "help_arch_server", ""),
    ("grp_arch", "arch-dev", (), "help_arch_dev", "[--user NAME]"),
    ("grp_arch", "arch-gaming", (), "help_arch_gaming", "[--user NAME]"),
]
NEEDS_BACKEND = {"install", "remove", "update", "upgrade", "search", "info",
                 "list", "clean", "autoremove", "alias", "distro",
                 "arch-install", "arch-config", "arch-desktop", "arch-server",
                 "arch-dev", "arch-gaming"}


def print_overview(backend_name: Optional[str] = None) -> None:
    ui.banner(backend_name)
    groups: dict = {}
    for grp, name, aliases_, help_key, args in COMMANDS:
        label = name + (" (%s)" % ", ".join(aliases_) if aliases_ else "")
        groups.setdefault(grp, []).append((label, args, t(help_key)))
    for grp, items in groups.items():
        ui.line(ui.paint(t(grp), "bold", "cyan"))
        width = max(ui.vlen(l) + ui.vlen(a) + 1 for l, a, _ in items)
        for label, args, desc in items:
            left = ui.paint(label, "green") + (" " + ui.paint(args, "gray") if args else "")
            ui.line("  " + ui.pad(left, width + 2 + (len(left) - ui.vlen(left))) + " " + desc)
        ui.line()
    ui.line(ui.paint(t("grp_options"), "bold", "cyan"))
    ui.line("  -y, --yes        " + t("opt_yes"))
    ui.line("  --dry-run        " + t("opt_dry_run"))
    ui.line("  --no-color       " + t("opt_no_color"))
    ui.line("  -V, --version    " + t("opt_version"))
    ui.line()
    ui.line(ui.paint("  " + t("overview_hint"), "gray"))
    ui.line()


class _HelpAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS, help=None):
        super().__init__(option_strings, dest, nargs=0, default=default, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print_overview()
        parser.exit()


def _common() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("-y", "--yes", action="store_true", default=argparse.SUPPRESS,
                   help=t("opt_yes"))
    p.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS,
                   help=t("opt_dry_run"))
    p.add_argument("--no-color", action="store_true", default=argparse.SUPPRESS,
                   help=t("opt_no_color"))
    return p


def build_parser() -> argparse.ArgumentParser:
    common = _common()
    parser = argparse.ArgumentParser(prog="dpa", add_help=False, parents=[common],
                                     description=t("desc"))
    parser.add_argument("-h", "--help", action=_HelpAction, help=t("opt_help"))
    parser.add_argument("-V", "--version", action="version",
                        version="dpa %s" % __version__, help=t("opt_version"))
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sp = {}
    for _, name, aliases_, help_key, _args in COMMANDS:
        sp[name] = sub.add_parser(name, aliases=list(aliases_), help=t(help_key),
                                  parents=[common])

    for name in ("install", "remove"):
        sp[name].add_argument("packages", nargs="+", metavar="PKG")
    sp["search"].add_argument("query", nargs="+", metavar="QUERY")
    sp["info"].add_argument("packages", nargs="+", metavar="PKG")
    sp["list"].add_argument("pattern", nargs="?", metavar="FILTER")
    sp["history"].add_argument("-n", "--limit", type=int, default=20,
                               help=t("opt_limit"))
    a = sp["alias"]
    a.add_argument("action", choices=["add", "list", "remove"])
    a.add_argument("names", nargs="*", metavar="NAME")
    a.add_argument("--alias", help=t("opt_alias_name"))
    a.add_argument("--real", help=t("opt_alias_real"))
    sp["lang"].add_argument("code", nargs="?", choices=list(SUPPORTED))
    sp["completion"].add_argument("shell", nargs="?", choices=list(completions.GENERATORS))
    sp["completion"].add_argument("--install", action="store_true",
                                  help=t("opt_comp_install"))
    sp["uninstall"].add_argument("extra", nargs="*", help=argparse.SUPPRESS)
    sp["uninstall"].add_argument("--keep-data", action="store_true",
                                 help=t("opt_keep_data"))

    for name in ("arch-install", "arch-desktop", "arch-server", "arch-dev",
                 "arch-gaming"):
        sp[name].add_argument("--target", default="/mnt", help=t("opt_target"))
    sp["arch-config"].add_argument("--target", default=None, help=t("opt_target_auto"))
    sp["arch-install"].add_argument("--packages", nargs="+", default=[],
                                    metavar="PKG", help=t("opt_extra_packages"))
    sp["arch-desktop"].add_argument("--de", default="gnome",
                                    choices=list(DESKTOPS), help=t("opt_de"))
    sp["arch-desktop"].add_argument("--no-gpu", action="store_true",
                                    help=t("opt_no_gpu"))
    sp["arch-server"].add_argument("--services", nargs="+", metavar="NAME",
                                   help=t("opt_services", ", ".join(CATEGORIES)))
    for name in ("arch-dev", "arch-gaming"):
        sp[name].add_argument("--user", help=t("opt_user"))
    sp["arch-gaming"].add_argument("--no-gpu", action="store_true",
                                   help=t("opt_no_gpu"))
    return parser


# ---------------------------------------------------------------- команды
def cmd_alias(args, svc: PackageService) -> bool:
    pm = svc.pm
    name = args.alias or (args.names[0] if args.names else None)
    real = args.real or (args.names[1] if len(args.names) > 1 else None)
    if args.action == "add":
        if not name or not real:
            ui.fail(t("alias_need_args"))
            return False
        svc.db.add_alias(name, real, pm)
        ui.ok(t("alias_added", name, real))
        return True
    if args.action == "remove":
        if not name:
            ui.fail(t("alias_need_args"))
            return False
        if svc.db.remove_alias(name, pm):
            ui.ok(t("alias_removed", name))
            return True
        ui.fail(t("alias_not_found", name))
        return False
    from .aliases import BUILTIN, builtin_for
    ui.section(t("alias_title", pm.upper()))
    rows = [(a, r, t("alias_type_custom")) for a, r in svc.db.list_aliases(pm)]
    rows += [(k, " ".join(builtin_for(k, pm)), t("alias_type_builtin"))
             for k in sorted(BUILTIN) if builtin_for(k, pm)]
    ui.table([t("col_alias"), t("col_package"), t("col_type")], rows)
    ui.line()
    ui.line(ui.paint("  " + t("alias_add_help"), "gray"))
    return True


def cmd_distro(svc: PackageService) -> bool:
    d = distro_info()
    ui.kv_box(t("distro_title"), [
        (t("lbl_distribution"), d.name),
        (t("lbl_pm"), svc.pm.upper()),
        (t("lbl_kernel"), kernel()),
        (t("lbl_arch"), platform.machine()),
        (t("lbl_python"), platform.python_version()),
        (t("lbl_dpa"), __version__),
        (t("lbl_language"), get_language()),
        (t("lbl_config"), str(config.config_dir())),
        (t("lbl_data"), str(config.data_dir())),
        (t("lbl_cache"), str(config.cache_dir())),
    ])
    return True


def cmd_history(args, svc: PackageService) -> bool:
    ui.section(t("history_title", args.limit))
    rows = svc.db.history(args.limit)
    if not rows:
        ui.info(t("history_empty"))
        return True
    out = []
    for r in rows:
        good = r["status"] == "success"
        mark = ui.paint(ui.sym("ok" if good else "fail"), "green" if good else "red")
        out.append((mark, r["timestamp"].replace("T", " "), r["command"],
                    " ".join(r["packages"]) or "-"))
    ui.table(["", t("col_time"), t("col_command"), t("col_packages")], out)
    return True


def cmd_lang(args, parser) -> bool:
    if not args.code:
        ui.line("  %s: %s" % (t("lbl_language"), get_language()))
        ui.line("  %s: %s" % (t("lang_available"), ", ".join(SUPPORTED)))
        return True
    data = config.load_config()
    data["language"] = args.code
    if not config.save_config(data):
        ui.fail(t("write_failed", config.config_file(), ""))
        return False
    set_language(args.code)
    selfmanage.refresh_completions(build_parser())
    ui.ok(t("lang_set", args.code))
    return True


def cmd_completion(args, parser) -> bool:
    if args.install or not args.shell:
        done = selfmanage.install_completions(parser)
        if done:
            ui.ok(t("completion_installed", ", ".join(done)))
            ui.info(t("completion_reload"))
        else:
            ui.warn(t("completion_none"))
        return True
    print(completions.GENERATORS[args.shell](parser), end="")
    return True


def cmd_uninstall(args) -> bool:
    if args.extra:
        ui.warn(t("uninstall_hint_remove"))
        return False
    return selfmanage.uninstall(keep_data=args.keep_data)


def dispatch(args, parser, backend) -> bool:
    cmd = _canonical(args.command)
    if cmd == "lang":
        return cmd_lang(args, parser)
    if cmd == "completion":
        return cmd_completion(args, parser)
    if cmd == "uninstall":
        return cmd_uninstall(args)
    svc = PackageService(backend, Database())
    table = {
        "install": lambda: svc.install(args.packages),
        "remove": lambda: svc.remove(args.packages),
        "update": svc.update,
        "upgrade": svc.upgrade,
        "search": lambda: svc.search(args.query),
        "info": lambda: svc.info(args.packages),
        "list": lambda: svc.list_installed(args.pattern),
        "clean": svc.clean,
        "autoremove": svc.autoremove,
        "history": lambda: cmd_history(args, svc),
        "alias": lambda: cmd_alias(args, svc),
        "distro": lambda: cmd_distro(svc),
        "arch-install": lambda: run_arch_install(svc.pm, args.target, args.packages),
        "arch-config": lambda: run_arch_config(svc.pm, args.target or default_target()),
        "arch-desktop": lambda: run_arch_desktop(svc.pm, args.de, args.target,
                                                 not args.no_gpu),
        "arch-server": lambda: run_arch_server(svc.pm, args.target, args.services),
        "arch-dev": lambda: run_arch_dev(svc.pm, args.target, args.user),
        "arch-gaming": lambda: run_arch_gaming(svc.pm, args.target, args.user,
                                               not args.no_gpu),
    }
    return table[cmd]()


def _canonical(name: str) -> str:
    for _, cmd, aliases_, _h, _a in COMMANDS:
        if name == cmd or name in aliases_:
            return cmd
    return name


def main(argv: Optional[List[str]] = None) -> int:
    set_language(config.resolve_language())
    parser = build_parser()
    args = parser.parse_args(argv)
    OPTS.dry_run = getattr(args, "dry_run", False)
    OPTS.assume_yes = getattr(args, "yes", False)
    if getattr(args, "no_color", False):
        ui.set_color(False)
    try:
        if not args.command:
            backend = detect()
            print_overview(backend.name.upper() if backend else None)
            return 0
        backend = None
        if _canonical(args.command) in NEEDS_BACKEND:
            backend = detect()
            if backend is None:
                ui.fail(t("error_pm"))
                return 1
        if OPTS.dry_run:
            ui.warn(t("dry_run_banner"))
        return 0 if dispatch(args, parser, backend) else 1
    except KeyboardInterrupt:
        print(t("interrupt"))
        return 130


def entry() -> None:
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:  # например, `dpa list | head`
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        code = 0
    sys.exit(code)


if __name__ == "__main__":
    entry()
