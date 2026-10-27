"""Высокоуровневые операции над пакетами: заголовки, алиасы, история."""
from __future__ import annotations

import time
from typing import Callable, List, Optional, Sequence

from . import aliases, ui
from .backends.base import Backend
from .db import Database
from .i18n import t
from .options import OPTS


class PackageService:
    def __init__(self, backend: Backend, db: Database):
        self.backend = backend
        self.db = db

    @property
    def pm(self) -> str:
        return self.backend.name

    def _check(self, names: Sequence[str]) -> bool:
        bad = [n for n in names if not aliases.valid_name(n)]
        for n in bad:
            ui.fail(t("invalid_package", n))
        return not bad

    def _run(self, title: str, fn: Callable[[], bool], ok_msg: str,
             log: Optional[str] = None, packages: Sequence[str] = ()) -> bool:
        ui.section(title)
        start = time.monotonic()
        success = fn()
        elapsed = time.monotonic() - start
        if log and not OPTS.dry_run:
            self.db.log(log, packages, "success" if success else "failed")
        ui.finish(success, ok_msg if success else t("failed"), elapsed)
        return success

    # --- операции ---
    def install(self, names: Sequence[str]) -> bool:
        if not self._check(names):
            return False
        ui.section(t("installing", " ".join(names)))
        pkgs = aliases.resolve(names, self.pm, self.db)
        start = time.monotonic()
        success = self.backend.install(pkgs, OPTS.assume_yes)
        if not OPTS.dry_run:
            self.db.log("install", names, "success" if success else "failed")
        ui.finish(success, t("completed", len(names)) if success else t("failed"),
                  time.monotonic() - start)
        return success

    def remove(self, names: Sequence[str]) -> bool:
        if not self._check(names):
            return False
        ui.section(t("removing", " ".join(names)))
        pkgs = aliases.resolve(names, self.pm, self.db)
        start = time.monotonic()
        success = self.backend.remove(pkgs, OPTS.assume_yes)
        if not OPTS.dry_run:
            self.db.log("remove", names, "success" if success else "failed")
        ui.finish(success, t("removed", len(names)) if success else t("failed"),
                  time.monotonic() - start)
        return success

    def update(self) -> bool:
        return self._run(t("updating"), self.backend.refresh, t("updated"),
                         "update")

    def upgrade(self) -> bool:
        return self._run(t("upgrading"),
                         lambda: self.backend.upgrade(OPTS.assume_yes),
                         t("upgraded"), "upgrade")

    def search(self, words: Sequence[str]) -> bool:
        query = " ".join(words)
        ui.section(t("searching", query))
        return self.backend.search(query)

    def info(self, names: Sequence[str]) -> bool:
        if not self._check(names):
            return False
        results: List[bool] = []
        for pkg in aliases.resolve(names, self.pm, self.db, announce=False):
            ui.section(t("info_pkg", pkg))
            results.append(self.backend.info(pkg))
        return all(results)

    def list_installed(self, pattern: Optional[str]) -> bool:
        ui.section(t("listing"))
        return self.backend.list_installed(pattern)

    def clean(self) -> bool:
        return self._run(t("cleaning"),
                         lambda: self.backend.clean(OPTS.assume_yes),
                         t("cleaned"), "clean")

    def autoremove(self) -> bool:
        return self._run(t("autoremoving"),
                         lambda: self.backend.autoremove(OPTS.assume_yes),
                         t("autoremoved"), "autoremove")
