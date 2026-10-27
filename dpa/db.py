"""SQLite: пользовательские алиасы и история транзакций."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from . import config, ui
from .i18n import t


class Database:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else config.data_dir() / "packages.db"
        self.available = True
        try:
            config.ensure_dir(self.path.parent)
            with closing(sqlite3.connect(self.path)) as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alias TEXT NOT NULL, real_name TEXT NOT NULL,
                    source TEXT NOT NULL, UNIQUE(alias, source))""")
                conn.execute("""CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL, command TEXT NOT NULL,
                    packages TEXT, status TEXT)""")
                conn.commit()
            config.fix_owner(self.path)
        except (sqlite3.Error, OSError) as exc:
            self.available = False
            ui.warn(t("db_unavailable", exc))

    def _exec(self, sql: str, params: Sequence = ()) -> List[Tuple]:
        if not self.available:
            return []
        try:
            with closing(sqlite3.connect(self.path)) as conn:
                rows = conn.execute(sql, params).fetchall()
                conn.commit()
                return rows
        except sqlite3.Error:
            return []

    # --- алиасы ---
    def add_alias(self, alias: str, real: str, source: str) -> None:
        self._exec("INSERT OR REPLACE INTO aliases (alias, real_name, source) "
                   "VALUES (?, ?, ?)", (alias, real, source))

    def remove_alias(self, alias: str, source: str) -> bool:
        before = self.get_alias(alias, source)
        self._exec("DELETE FROM aliases WHERE alias = ? AND source = ?",
                   (alias, source))
        return before is not None

    def get_alias(self, alias: str, source: str) -> Optional[str]:
        rows = self._exec("SELECT real_name FROM aliases WHERE alias = ? "
                          "AND source = ?", (alias, source))
        return rows[0][0] if rows else None

    def list_aliases(self, source: str) -> List[Tuple[str, str]]:
        return [(a, r) for a, r in self._exec(
            "SELECT alias, real_name FROM aliases WHERE source = ? "
            "ORDER BY alias", (source,))]

    # --- история ---
    def log(self, command: str, packages: Sequence[str], status: str) -> None:
        self._exec("INSERT INTO history (timestamp, command, packages, status) "
                   "VALUES (?, ?, ?, ?)",
                   (datetime.now().isoformat(timespec="seconds"), command,
                    json.dumps(list(packages), ensure_ascii=False), status))

    def history(self, limit: int = 20) -> List[Dict]:
        rows = self._exec("SELECT timestamp, command, packages, status FROM "
                          "history ORDER BY id DESC LIMIT ?", (limit,))
        out = []
        for ts, cmd, pk, st in rows:
            try:
                pkgs = json.loads(pk) if pk else []
            except ValueError:
                pkgs = []
            out.append({"timestamp": ts, "command": cmd, "packages": pkgs,
                        "status": st})
        return out
