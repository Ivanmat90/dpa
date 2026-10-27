"""Переводы. Каталоги лежат в dpa/locales/<код>.py (словарь STRINGS)."""
from __future__ import annotations

import importlib
from typing import Dict

SUPPORTED = ("en", "ru")
DEFAULT = "en"

_lang = DEFAULT
_catalogs: Dict[str, Dict[str, str]] = {}


def catalog(code: str) -> Dict[str, str]:
    if code not in _catalogs:
        module = importlib.import_module("dpa.locales." + code)
        _catalogs[code] = module.STRINGS
    return _catalogs[code]


def set_language(code: str) -> None:
    global _lang
    _lang = code if code in SUPPORTED else DEFAULT


def get_language() -> str:
    return _lang


def t(key: str, *args, **kwargs) -> str:
    """Строка на текущем языке; при отсутствии - английская, затем сам ключ."""
    text = catalog(_lang).get(key)
    if text is None:
        text = catalog(DEFAULT).get(key, key)
    if args or kwargs:
        try:
            return text.format(*args, **kwargs)
        except (IndexError, KeyError, ValueError):
            return text
    return text
