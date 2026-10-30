"""Textual-интерфейс DPA. Импортируется только когда Textual установлен.

Слой намеренно тонкий: вся логика (поиск, разбор вывода, алиасы, история)
живёт в model.py и backends/ и проверена тестами без Textual.

Изменяющие систему операции (install/remove/upgrade...) выполняются через
App.suspend(): TUI временно уступает терминал, поэтому работают запрос
пароля sudo и подтверждения самого менеджера пакетов.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from rich.markup import escape
from rich.table import Table
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (Button, DataTable, Footer, Header, Input, Label,
                             Static, TabbedContent, TabPane)

from .. import __version__, config
from ..backends.base import PackageHit
from ..i18n import SUPPORTED, get_language, t
from ..manager import PackageService
from ..options import OPTS
from .model import TuiModel

CSS = """
Screen { background: $surface; }
TabbedContent { height: 1fr; }
TabPane { padding: 0 1; }

.searchbar { height: 3; margin-bottom: 1; }
.searchbar Input { width: 1fr; }
.searchbar Button { margin-left: 1; }

.body { height: 1fr; }
.table { height: 1fr; }
#pkg-table { width: 3fr; }
.infobox { width: 2fr; height: 1fr; border: round $primary; padding: 0 1; margin-left: 1; }

.actions { height: 3; margin-top: 1; }
.actions Button { margin-right: 1; }
.status { padding: 1 1; color: $text-muted; }

.title { text-style: bold; color: $accent; margin: 1 0 0 0; }
.hint { color: $text-muted; }
.sysinfo { height: auto; padding: 1 2; border: round $primary; margin-bottom: 1; }
.bigbuttons { height: auto; }
.bigbuttons Button { margin-right: 2; }
.formrow { height: 3; margin-top: 1; }
.formrow Input { width: 1fr; margin-right: 1; }

ConfirmScreen { align: center middle; }
#confirm-box { width: 64; max-width: 90%; height: auto; border: thick $primary;
               background: $panel; padding: 1 2; }
#confirm-title { text-style: bold; margin-bottom: 1; }
#confirm-body { margin-bottom: 1; }
#confirm-hint { color: $text-muted; margin-bottom: 1; }
#confirm-buttons { height: auto; align-horizontal: right; }
#confirm-buttons Button { margin-left: 2; }
"""


def _typing(app: App) -> bool:
    """Идёт ввод текста: однобуквенные горячие клавиши не трогаем."""
    return isinstance(app.focused, Input)


# ---------------------------------------------------------------- диалог
class ConfirmScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "cancel", t("tui_cancel")),
        Binding("y", "confirm", t("tui_yes"), show=False),
        Binding("n", "cancel", t("tui_cancel"), show=False),
    ]

    def __init__(self, title: str, lines: Sequence[str], yes_label: str,
                 danger: bool = False, hint: str = ""):
        super().__init__()
        self._dlg_title, self._dlg_lines = title, list(lines)
        self._dlg_yes, self._dlg_danger, self._dlg_hint = yes_label, danger, hint

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Static(Text(self._dlg_title), id="confirm-title")
            if self._dlg_lines:
                yield Static(Text("\n".join(self._dlg_lines)), id="confirm-body")
            if self._dlg_hint:
                yield Static(Text(self._dlg_hint), id="confirm-hint")
            with Horizontal(id="confirm-buttons"):
                yield Button(self._dlg_yes, id="confirm-yes",
                             variant="error" if self._dlg_danger else "success")
                yield Button(t("tui_cancel"), id="confirm-no")

    @on(Button.Pressed, "#confirm-yes")
    def _pressed_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirm-no")
    def _pressed_no(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


# ---------------------------------------------------------------- пакеты
class PackageTable(DataTable):
    """Таблица результатов. Клавиши действуют только когда она в фокусе,
    поэтому не мешают вводу в строку поиска."""
    BINDINGS = [
        Binding("space", "toggle_mark", t("tui_mark")),
        Binding("i", "install", t("tui_install")),
        Binding("r", "remove", t("tui_remove")),
    ]

    def action_toggle_mark(self) -> None:
        self.screen.query_one(PackagesPanel).toggle_mark()

    def action_install(self) -> None:
        self.screen.query_one(PackagesPanel).do_install()

    def action_remove(self) -> None:
        self.screen.query_one(PackagesPanel).do_remove()


class PackagesPanel(Vertical):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hits: Dict[str, PackageHit] = {}
        self.marked: set = set()
        self._state_col = None
        self._info_timer = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="searchbar"):
            yield Input(placeholder=t("tui_search_placeholder"), id="pkg-query")
            yield Button(t("tui_search"), id="pkg-search", variant="primary")
        with Horizontal(classes="body"):
            yield PackageTable(id="pkg-table", classes="table",
                               cursor_type="row", zebra_stripes=True)
            with VerticalScroll(classes="infobox"):
                yield Static(Text(t("tui_info_empty")), id="pkg-info")
        with Horizontal(classes="actions"):
            yield Button(t("tui_install"), id="pkg-install", variant="success")
            yield Button(t("tui_remove"), id="pkg-remove", variant="error")
            yield Button(t("tui_mark"), id="pkg-mark")
            yield Button(t("tui_clear_marks"), id="pkg-clear")
            yield Label(t("tui_hint_search"), id="pkg-status", classes="status")

    def on_mount(self) -> None:
        table = self.query_one("#pkg-table", DataTable)
        self._state_col = table.add_column(t("tui_col_status"), width=3)
        table.add_column(t("tui_col_name"))
        table.add_column(t("tui_col_version"))
        table.add_column(t("tui_col_desc"))

    # --- вспомогательное ---
    def _status(self, text: str) -> None:
        self.query_one("#pkg-status", Label).update(text)

    def _state_cell(self, hit: PackageHit) -> Text:
        cell = Text()
        cell.append("◆" if hit.name in self.marked else " ", style="bold yellow")
        cell.append("✔" if hit.installed else " ", style="bold green")
        return cell

    def _current_name(self) -> Optional[str]:
        table = self.query_one("#pkg-table", DataTable)
        names = list(self.hits)
        index = table.cursor_row
        return names[index] if 0 <= index < len(names) else None

    def selected(self) -> List[PackageHit]:
        if self.marked:
            return [self.hits[n] for n in self.hits if n in self.marked]
        name = self._current_name()
        return [self.hits[name]] if name else []

    # --- поиск ---
    @on(Input.Submitted, "#pkg-query")
    def _submitted(self) -> None:
        self.start_search()

    @on(Button.Pressed, "#pkg-search")
    def _search_pressed(self) -> None:
        self.start_search()

    def start_search(self) -> None:
        query = self.query_one("#pkg-query", Input).value.strip()
        if not query:
            return
        self._status(t("tui_searching"))
        self._search(query)

    @work(thread=True, exclusive=True, group="search")
    def _search(self, query: str) -> None:
        try:
            hits = self.app.model.search(query)
        except Exception as exc:  # noqa: BLE001 - показываем, а не роняем TUI
            self.app.call_from_thread(self.app.notify, escape(str(exc)), severity="error")
            return
        self.app.call_from_thread(self._fill, hits)

    def _fill(self, hits: List[PackageHit]) -> None:
        table = self.query_one("#pkg-table", DataTable)
        table.clear()
        self.hits = {h.name: h for h in hits}
        self.marked &= set(self.hits)
        for hit in self.hits.values():
            table.add_row(self._state_cell(hit), hit.name, hit.version,
                          hit.description, key=hit.name)
        if self.hits:
            self._status(t("tui_found", len(self.hits)))
            table.focus()
        else:
            self._status(t("tui_nothing"))
            self.query_one("#pkg-info", Static).update(Text(t("tui_info_empty")))

    # --- информация о выбранном пакете ---
    @on(DataTable.RowHighlighted, "#pkg-table")
    def _highlighted(self, event: DataTable.RowHighlighted) -> None:
        name = getattr(getattr(event, "row_key", None), "value", None)
        if not name:
            return
        if self._info_timer is not None:
            self._info_timer.stop()
        self._info_timer = self.set_timer(0.3, lambda n=name: self._load_info(n))

    @work(thread=True, exclusive=True, group="info")
    def _load_info(self, name: str) -> None:
        text = self.app.model.info(name)
        self.app.call_from_thread(self._show_info, name, text)

    def _show_info(self, name: str, text: str) -> None:
        if name == self._current_name():
            self.query_one("#pkg-info", Static).update(Text(text or name))

    # --- отметки и действия ---
    def toggle_mark(self) -> None:
        name = self._current_name()
        if not name:
            return
        if name in self.marked:
            self.marked.discard(name)
        else:
            self.marked.add(name)
        table = self.query_one("#pkg-table", DataTable)
        table.update_cell(name, self._state_col, self._state_cell(self.hits[name]))
        self._status(t("tui_marked", len(self.marked)) if self.marked else "")
        table.action_cursor_down()

    @on(Button.Pressed, "#pkg-mark")
    def _mark_pressed(self) -> None:
        self.toggle_mark()

    @on(Button.Pressed, "#pkg-clear")
    def _clear_pressed(self) -> None:
        table = self.query_one("#pkg-table", DataTable)
        for name in list(self.marked):
            self.marked.discard(name)
            table.update_cell(name, self._state_col, self._state_cell(self.hits[name]))
        self._status("")

    @on(Button.Pressed, "#pkg-install")
    def _install_pressed(self) -> None:
        self.do_install()

    @on(Button.Pressed, "#pkg-remove")
    def _remove_pressed(self) -> None:
        self.do_remove()

    def do_install(self) -> None:
        picked = self.selected()
        if not picked:
            self.app.notify(t("tui_no_selection"), severity="warning")
            return
        names = [h.name for h in picked if not h.installed]
        if not names:
            self.app.notify(t("tui_already_installed"), severity="information")
            return
        self.app.run_op("install", names)

    def do_remove(self) -> None:
        picked = self.selected()
        if not picked:
            self.app.notify(t("tui_no_selection"), severity="warning")
            return
        names = [h.name for h in picked if h.installed]
        if not names:
            self.app.notify(t("tui_not_installed"), severity="information")
            return
        self.app.run_op("remove", names)

    def refresh_data(self) -> None:
        """После операции перечитываем отметки установки (в потоке)."""
        if self.hits:
            self._reload_installed()

    @work(thread=True, exclusive=True, group="reinstalled")
    def _reload_installed(self) -> None:
        installed = self.app.model.installed()
        self.app.call_from_thread(self._apply_installed, installed)

    def _apply_installed(self, installed: dict) -> None:
        table = self.query_one("#pkg-table", DataTable)
        for name, hit in self.hits.items():
            hit.installed = name in installed
            table.update_cell(name, self._state_col, self._state_cell(hit))


# ---------------------------------------------------------------- установленные
class InstalledPanel(Vertical):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._inst_all: List[tuple] = []
        self._inst_shown: List[str] = []

    def compose(self) -> ComposeResult:
        with Horizontal(classes="searchbar"):
            yield Input(placeholder=t("tui_filter_placeholder"), id="inst-filter")
            yield Button(t("tui_refresh"), id="inst-refresh")
        yield DataTable(id="inst-table", classes="table", cursor_type="row",
                        zebra_stripes=True)
        with Horizontal(classes="actions"):
            yield Button(t("tui_remove"), id="inst-remove", variant="error")
            yield Label("", id="inst-status", classes="status")

    def on_mount(self) -> None:
        table = self.query_one("#inst-table", DataTable)
        table.add_column(t("tui_col_name"))
        table.add_column(t("tui_col_version"))

    def refresh_data(self) -> None:
        self.query_one("#inst-status", Label).update(t("tui_loading"))
        self._load()

    @work(thread=True, exclusive=True, group="installed")
    def _load(self) -> None:
        data = self.app.model.installed(refresh=True)
        self.app.call_from_thread(self._fill, sorted(data.items()))

    def _fill(self, rows: List[tuple]) -> None:
        self._inst_all = rows
        self._apply_filter()

    @on(Input.Changed, "#inst-filter")
    def _filter_changed(self) -> None:
        self._apply_filter()

    def _apply_filter(self) -> None:
        needle = self.query_one("#inst-filter", Input).value.strip().lower()
        matches = [r for r in self._inst_all if needle in r[0].lower()]
        shown = matches[:1000]
        table = self.query_one("#inst-table", DataTable)
        table.clear()
        self._inst_shown = []
        for name, version in shown:
            table.add_row(name, version, key=name)
            self._inst_shown.append(name)
        self.query_one("#inst-status", Label).update(
            t("tui_shown", len(shown), len(self._inst_all)))

    @on(Button.Pressed, "#inst-refresh")
    def _refresh_pressed(self) -> None:
        self.refresh_data()

    @on(Button.Pressed, "#inst-remove")
    def _remove_pressed(self) -> None:
        index = self.query_one("#inst-table", DataTable).cursor_row
        if 0 <= index < len(self._inst_shown):
            self.app.run_op("remove", [self._inst_shown[index]])
        else:
            self.app.notify(t("tui_no_selection"), severity="warning")


# ---------------------------------------------------------------- система
class SystemPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Static(Text(""), id="sys-info", classes="sysinfo")
        yield Static(Text(t("tui_actions")), classes="title")
        with Horizontal(classes="bigbuttons"):
            yield Button(t("tui_btn_update"), id="sys-update", variant="primary")
            yield Button(t("tui_btn_upgrade"), id="sys-upgrade", variant="success")
            yield Button(t("tui_btn_clean"), id="sys-clean")
            yield Button(t("tui_btn_autoremove"), id="sys-autoremove", variant="warning")

    def refresh_data(self) -> None:
        grid = Table.grid(padding=(0, 2))
        for key, value in self.app.model.system_info():
            grid.add_row(Text(t("tui_sys_" + key), style="dim"), Text(str(value)))
        self.query_one("#sys-info", Static).update(grid)

    def on_mount(self) -> None:
        self.refresh_data()

    @on(Button.Pressed, "#sys-update")
    def _update(self) -> None:
        self.app.run_op("update")

    @on(Button.Pressed, "#sys-upgrade")
    def _upgrade(self) -> None:
        self.app.run_op("upgrade")

    @on(Button.Pressed, "#sys-clean")
    def _clean(self) -> None:
        self.app.run_op("clean")

    @on(Button.Pressed, "#sys-autoremove")
    def _autoremove(self) -> None:
        self.app.run_op("autoremove")


# ---------------------------------------------------------------- история
class HistoryPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield DataTable(id="hist-table", classes="table", cursor_type="row",
                        zebra_stripes=True)
        yield Label("", id="hist-status", classes="status")

    def on_mount(self) -> None:
        table = self.query_one("#hist-table", DataTable)
        table.add_column(t("tui_col_status"), width=3)
        table.add_column(t("col_time"))
        table.add_column(t("col_command"))
        table.add_column(t("col_packages"))
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#hist-table", DataTable)
        table.clear()
        rows = self.app.model.history()
        for row in rows:
            good = row["status"] == "success"
            mark = Text("✔" if good else "✖", style="bold green" if good else "bold red")
            table.add_row(mark, row["timestamp"].replace("T", " "), row["command"],
                          " ".join(row["packages"]) or "-")
        self.query_one("#hist-status", Label).update("" if rows else t("tui_history_empty"))


# ---------------------------------------------------------------- алиасы
class AliasesPanel(Vertical):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alias_rows: List[tuple] = []

    def compose(self) -> ComposeResult:
        yield DataTable(id="alias-table", classes="table", cursor_type="row",
                        zebra_stripes=True)
        with Horizontal(classes="formrow"):
            yield Input(placeholder=t("tui_alias_name"), id="alias-name")
            yield Input(placeholder=t("tui_alias_target"), id="alias-target")
            yield Button(t("tui_add"), id="alias-add", variant="success")
            yield Button(t("tui_remove"), id="alias-remove", variant="error")

    def on_mount(self) -> None:
        table = self.query_one("#alias-table", DataTable)
        table.add_column(t("tui_alias_name"))
        table.add_column(t("tui_alias_target"))
        table.add_column(t("col_type"))
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#alias-table", DataTable)
        table.clear()
        self._alias_rows = self.app.model.alias_rows()
        for alias, target, kind in self._alias_rows:
            table.add_row(alias, target, t("tui_alias_type_" + kind))

    @on(Button.Pressed, "#alias-add")
    def _add(self) -> None:
        name = self.query_one("#alias-name", Input).value.strip()
        target = self.query_one("#alias-target", Input).value.strip()
        if self.app.model.add_alias(name, target):
            self.app.notify(t("tui_alias_added", name))
            self.query_one("#alias-name", Input).value = ""
            self.query_one("#alias-target", Input).value = ""
            self.refresh_data()
        else:
            self.app.notify(t("tui_alias_invalid"), severity="error")

    @on(Button.Pressed, "#alias-remove")
    def _remove(self) -> None:
        index = self.query_one("#alias-table", DataTable).cursor_row
        if not 0 <= index < len(self._alias_rows):
            self.app.notify(t("tui_no_selection"), severity="warning")
            return
        alias, _target, kind = self._alias_rows[index]
        if kind != "custom":
            self.app.notify(t("tui_alias_builtin"), severity="warning")
            return
        self.app.model.remove_alias(alias)
        self.refresh_data()


# ---------------------------------------------------------------- настройки
class SettingsPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Static(Text(t("tui_settings_lang")), classes="title")
        with Horizontal(classes="bigbuttons"):
            yield Button("English", id="lang-en",
                         variant="primary" if get_language() == "en" else "default")
            yield Button("Русский", id="lang-ru",
                         variant="primary" if get_language() == "ru" else "default")
        yield Static(Text(t("tui_key_hint")), classes="hint")
        yield Static(Text("DPA %s" % __version__), classes="hint")

    @on(Button.Pressed, "#lang-en")
    def _en(self) -> None:
        self.app.set_language("en")

    @on(Button.Pressed, "#lang-ru")
    def _ru(self) -> None:
        self.app.set_language("ru")


# ---------------------------------------------------------------- приложение
TAB_PANELS = {"tab-installed": "#panel-installed", "tab-system": "#panel-system",
              "tab-history": "#panel-history", "tab-aliases": "#panel-aliases"}


class DpaApp(App):
    TITLE = "DPA"
    CSS = CSS
    BINDINGS = [
        Binding("ctrl+q", "quit", t("tui_quit")),
        Binding("q", "quit_key", t("tui_quit"), show=False),
        Binding("slash", "focus_search", t("tui_search")),
        Binding("f5", "refresh", t("tui_refresh")),
        Binding("1", "goto('tab-packages')", show=False),
        Binding("2", "goto('tab-installed')", show=False),
        Binding("3", "goto('tab-system')", show=False),
        Binding("4", "goto('tab-history')", show=False),
        Binding("5", "goto('tab-aliases')", show=False),
        Binding("6", "goto('tab-settings')", show=False),
    ]

    def __init__(self, model: TuiModel, service: PackageService):
        super().__init__()
        self.model = model
        self.service = service

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="tab-packages", id="tabs"):
            with TabPane(t("tui_tab_packages"), id="tab-packages"):
                yield PackagesPanel(id="panel-packages")
            with TabPane(t("tui_tab_installed"), id="tab-installed"):
                yield InstalledPanel(id="panel-installed")
            with TabPane(t("tui_tab_system"), id="tab-system"):
                yield SystemPanel(id="panel-system")
            with TabPane(t("tui_tab_history"), id="tab-history"):
                yield HistoryPanel(id="panel-history")
            with TabPane(t("tui_tab_aliases"), id="tab-aliases"):
                yield AliasesPanel(id="panel-aliases")
            with TabPane(t("tui_tab_settings"), id="tab-settings"):
                yield SettingsPanel(id="panel-settings")
        yield Footer()

    def on_mount(self) -> None:
        sub = "%s  ·  %s" % (self.model.system_info()[0][1], self.model.pm.upper())
        if OPTS.dry_run:
            sub += "  ·  " + t("tui_dry_run")
        self.sub_title = sub
        self.query_one("#pkg-query", Input).focus()

    # --- навигация ---
    def action_goto(self, tab_id: str) -> None:
        if _typing(self):
            return
        self.query_one(TabbedContent).active = tab_id

    def action_focus_search(self) -> None:
        if _typing(self):
            return
        self.query_one(TabbedContent).active = "tab-packages"
        self.query_one("#pkg-query", Input).focus()

    def action_quit_key(self) -> None:
        if not _typing(self):
            self.exit()

    def action_refresh(self) -> None:
        self.refresh_all()

    @on(TabbedContent.TabActivated)
    def _tab_changed(self, event: TabbedContent.TabActivated) -> None:
        pane = getattr(event, "pane", None)
        selector = TAB_PANELS.get(getattr(pane, "id", None) or "")
        if selector:
            self.query_one(selector).refresh_data()

    def refresh_all(self) -> None:
        self.model.invalidate()
        for selector in TAB_PANELS.values():
            try:
                self.query_one(selector).refresh_data()
            except Exception:  # noqa: BLE001
                pass
        self.query_one(PackagesPanel).refresh_data()

    # --- операции ---
    def run_op(self, kind: str, names: Sequence[str] = ()) -> None:
        svc = self.service
        names = list(names)
        plan = {
            "install": (t("tui_confirm_install", len(names)), False,
                        lambda: svc.install(names)),
            "remove": (t("tui_confirm_remove", len(names)), True,
                       lambda: svc.remove(names)),
            "update": (t("tui_confirm_update"), False, svc.update),
            "upgrade": (t("tui_confirm_upgrade"), False, svc.upgrade),
            "clean": (t("tui_confirm_clean"), False, svc.clean),
            "autoremove": (t("tui_confirm_autoremove"), True, svc.autoremove),
        }
        title, danger, action = plan[kind]

        def after(confirmed: Optional[bool]) -> None:
            if confirmed:
                self.run_in_terminal(action)

        self.push_screen(ConfirmScreen(title, names, t("tui_yes"), danger,
                                       hint=t("tui_run_hint")), after)

    def run_in_terminal(self, action) -> None:
        """Уступаем терминал: так работают пароль sudo и вопросы pacman/apt."""
        try:
            with self.suspend():
                print()
                action()
                print()
                try:
                    input(t("tui_press_enter"))
                except EOFError:
                    pass
        except Exception as exc:  # noqa: BLE001
            self.notify(escape(t("tui_run_failed", exc)), severity="error")
        self.refresh_all()

    # --- настройки ---
    def set_language(self, code: str) -> None:
        if code not in SUPPORTED:
            return
        data = config.load_config()
        data["language"] = code
        config.save_config(data)
        self.notify(t("tui_lang_saved"))


def run_app(backend, db) -> bool:
    model = TuiModel(backend, db)
    DpaApp(model, PackageService(backend, db)).run()
    return True
