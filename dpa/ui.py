"""Оформление вывода: цвета, иконки, баннер, таблицы, вопросы. Без зависимостей.

Учитывает NO_COLOR / FORCE_COLOR, не-TTY и консоль без Unicode (TERM=linux).
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import unicodedata
from typing import Iterable, List, Optional, Sequence

from . import __version__
from .i18n import t
from .options import OPTS

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_CODES = {"reset": "0", "bold": "1", "dim": "2", "red": "31", "green": "32",
          "yellow": "33", "blue": "34", "magenta": "35", "cyan": "36",
          "gray": "90"}
_color_override: Optional[bool] = None


def set_color(value: Optional[bool]) -> None:
    global _color_override
    _color_override = value


def color_enabled(stream=None) -> bool:
    stream = stream or sys.stdout
    if _color_override is not None:
        return _color_override
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    isatty = getattr(stream, "isatty", lambda: False)()
    return bool(isatty) and os.environ.get("TERM", "") != "dumb"


def paint(text: str, *styles: str, stream=None) -> str:
    if not styles or not color_enabled(stream):
        return text
    codes = ";".join(_CODES[s] for s in styles)
    return "\x1b[%sm%s\x1b[0m" % (codes, text)


def unicode_ok(stream=None) -> bool:
    enc = (getattr(stream or sys.stdout, "encoding", None) or "").lower()
    return "utf" in enc and os.environ.get("TERM", "") != "linux"


_UNI = {"ok": "✔", "fail": "✖", "warn": "▲", "info": "•", "dry": "◌",
        "arrow": "▸", "h": "─", "v": "│", "tl": "╭", "tr": "╮", "bl": "╰",
        "br": "╯", "ask": "?", "dot": "·"}
_ASC = {"ok": "[+]", "fail": "[x]", "warn": "[!]", "info": "[i]", "dry": "[~]",
        "arrow": ">", "h": "-", "v": "|", "tl": "+", "tr": "+", "bl": "+",
        "br": "+", "ask": "?", "dot": "-"}


def sym(name: str) -> str:
    return (_UNI if unicode_ok() else _ASC)[name]


def vlen(text: str) -> int:
    """Видимая ширина строки (без ANSI, с учётом широких символов)."""
    width = 0
    for ch in _ANSI.sub("", text):
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def pad(text: str, width: int) -> str:
    return text + " " * max(0, width - vlen(text))


def term_width(default: int = 80) -> int:
    return max(40, min(shutil.get_terminal_size((default, 24)).columns, 100))


def line(msg: str = "", stream=None) -> None:
    print(msg, file=stream or sys.stdout, flush=True)


def _emit(icon: str, style: str, msg: str, stream=None) -> None:
    stream = stream or sys.stdout
    print("  %s %s" % (paint(sym(icon), style, "bold", stream=stream), msg),
          file=stream, flush=True)


def ok(msg: str) -> None:
    _emit("ok", "green", msg)


def info(msg: str) -> None:
    _emit("info", "cyan", msg)


def warn(msg: str) -> None:
    _emit("warn", "yellow", msg)


def fail(msg: str) -> None:
    _emit("fail", "red", msg, sys.stderr)


def dry(msg: str) -> None:
    _emit("dry", "magenta", paint("[dry-run] ", "magenta") + msg)


def command_line(argv: Sequence[str]) -> None:
    text = " ".join(str(a) for a in argv)
    print("  " + paint("$ " + text, "gray"), flush=True)


def section(title: str) -> None:
    width = min(term_width(), 64)
    print()
    print(paint(sym("arrow") + " " + title, "cyan", "bold"))
    print(paint(sym("h") * width, "gray"), flush=True)


def human_time(seconds: float) -> str:
    if seconds < 60:
        return "%.1f s" % seconds
    minutes, sec = divmod(int(seconds), 60)
    return "%d:%02d" % (minutes, sec)


def finish(success: bool, message: str, seconds: Optional[float] = None) -> None:
    if success:
        tail = ""
        if seconds is not None and seconds >= 0.5:
            tail = " " + paint("(%s)" % human_time(seconds), "gray")
        ok(message + tail)
    else:
        fail(message)


def box(title: str, rows: Iterable[str]) -> None:
    rows = list(rows)
    inner = max([vlen(r) for r in rows] + [vlen(title) + 2]) + 2
    print(paint(sym("tl") + sym("h") + " ", "gray")
          + paint(title, "bold", "cyan")
          + paint(" " + sym("h") * (inner - vlen(title) - 3) + sym("tr"), "gray"))
    for row in rows:
        print(paint(sym("v"), "gray") + " " + pad(row, inner - 2) + " "
              + paint(sym("v"), "gray"))
    print(paint(sym("bl") + sym("h") * inner + sym("br"), "gray"), flush=True)


def kv_box(title: str, pairs: Sequence[Sequence[str]]) -> None:
    width = max(vlen(k) for k, _ in pairs)
    box(title, [paint(pad(k, width), "gray") + "  " + str(v) for k, v in pairs])


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    cols = len(headers)
    widths = [vlen(h) for h in headers]
    for row in rows:
        for i in range(cols):
            widths[i] = max(widths[i], vlen(str(row[i])))
    print("  " + "  ".join(paint(pad(h, widths[i]), "bold")
                           for i, h in enumerate(headers)))
    print("  " + paint("  ".join(sym("h") * w for w in widths), "gray"))
    for row in rows:
        print("  " + "  ".join(pad(str(row[i]), widths[i]) for i in range(cols)))
    sys.stdout.flush()


def bullets(items: Iterable[str]) -> None:
    for item in items:
        print("    " + paint(sym("dot"), "gray") + " " + item)
    sys.stdout.flush()


_BANNER = [
    "  ██████████   ███████████    █████████",
    " ▒▒███▒▒▒▒███ ▒▒███▒▒▒▒▒███  ███▒▒▒▒▒███",
    "  ▒███   ▒▒███ ▒███    ▒███ ▒███    ▒███",
    "  ▒███    ▒███ ▒██████████  ▒███████████",
    "  ▒███    ▒███ ▒███▒▒▒▒▒▒   ▒███▒▒▒▒▒███",
    "  ▒███    ███  ▒███         ▒███    ▒███",
    "  ██████████   █████        █████   █████",
    " ▒▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒        ▒▒▒▒▒   ▒▒▒▒▒",
]


def banner(backend: Optional[str] = None) -> None:
    print()
    if unicode_ok():
        for row in _BANNER:
            print(paint(row, "cyan"))
    else:
        print(paint("  D P A", "cyan", "bold"))
    sub = "v%s  %s  apt | dnf | pacman" % (__version__, sym("dot"))
    if backend:
        sub += "  %s  %s: %s" % (sym("dot"), t("lbl_backend"), backend)
    print(paint("  " + t("banner_tagline"), "bold"))
    print(paint("  " + sub, "gray"))
    print(paint("  https://github.com/Ivanmat90/dpa", "gray"))
    print(flush=True)


def _yn_hint(default: bool) -> str:
    return t("yn_yes_default") if default else t("yn_no_default")


def confirm(question: str, default: bool = False) -> bool:
    if OPTS.assume_yes or OPTS.dry_run:
        return True
    if not sys.stdin.isatty():
        warn(t("confirm_noninteractive"))
        return default
    try:
        answer = input("  %s %s %s " % (paint(sym("ask"), "yellow", "bold"),
                                        question, _yn_hint(default)))
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    answer = answer.strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes", "д", "да")


def prompt(text: str, default: str = "") -> str:
    hint = " [%s]" % default if default else ""
    try:
        value = input("  %s %s%s: " % (paint(sym("ask"), "yellow", "bold"),
                                       text, hint))
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return value.strip() or default
