"""Тесты TUI. Всё, что не требует Textual, выполняется всегда;
тесты на настоящем Textual запускаются, только если он установлен."""
import importlib
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import types
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dpa import i18n  # noqa: E402
from dpa.backends.apt import AptBackend  # noqa: E402
from dpa.backends.base import PackageHit  # noqa: E402
from dpa.backends.dnf import DnfBackend  # noqa: E402
from dpa.backends.pacman import PacmanBackend  # noqa: E402
from dpa.db import Database  # noqa: E402
from dpa.options import OPTS  # noqa: E402
from dpa.tui import deps, launch  # noqa: E402
from dpa.tui.model import TuiModel, rank  # noqa: E402


class ParserTests(unittest.TestCase):
    def test_apt_search(self):
        hits = AptBackend().parse_search(
            "vlc - multimedia player and streamer\nvlc-bin - binaries from VLC\n"
            "W: some warning line\n")
        self.assertEqual([h.name for h in hits], ["vlc", "vlc-bin"])
        self.assertEqual(hits[0].description, "multimedia player and streamer")

    def test_apt_installed_skips_removed_config(self):
        out = "ii \tbash\t5.2\nrc \toldpkg\t1.0\nii \tvim\t9.0\n"
        self.assertEqual(AptBackend().parse_installed(out), {"bash": "5.2", "vim": "9.0"})

    def test_pacman_search(self):
        out = ("extra/vlc 3.0.21-1 [installed]\n    A multi-platform player\n"
               "multilib/lib32-x 1.0-1 (group)\n    lib32 thing\n")
        hits = PacmanBackend().parse_search(out)
        self.assertEqual([(h.name, h.version, h.installed) for h in hits],
                         [("vlc", "3.0.21-1", True), ("lib32-x", "1.0-1", False)])
        self.assertEqual(hits[1].description, "lib32 thing")

    def test_pacman_installed(self):
        self.assertEqual(PacmanBackend().parse_installed("bash 5.2.037-1\nvim 9.1-1\n"),
                         {"bash": "5.2.037-1", "vim": "9.1-1"})

    def test_dnf_search_both_formats(self):
        out = ("=== Name & Summary Matched: vlc ===\n"
               "vlc.x86_64 : The cross-platform framework\n"
               "vlc-core.x86_64 : VLC core\n"
               "Matched fields: name\n"
               " vlc-extras.noarch   dnf5 style summary\n")
        names = [h.name for h in DnfBackend().parse_search(out)]
        self.assertEqual(names, ["vlc", "vlc-core", "vlc-extras"])

    def test_dnf_installed(self):
        self.assertEqual(DnfBackend().parse_installed("bash\t5.2-1.fc40\nvim\t9.1-2\n"),
                         {"bash": "5.2-1.fc40", "vim": "9.1-2"})

    def test_search_hits_dedupes_and_ignores_exit_code(self):
        b = PacmanBackend()
        out = "extra/a 1-1\n    d\nmultilib/a 1-1\n    d2\n"
        with mock.patch("dpa.backends.base.run",
                        return_value=mock.Mock(ok=False, stdout=out)):
            self.assertEqual([h.name for h in b.search_hits("a")], ["a"])


class FakeBackend:
    name = "apt"

    def __init__(self):
        self.calls = 0

    def search_hits(self, q):
        return [PackageHit("libvlc", "", "lib"), PackageHit("vlc-bin", "", "bin"),
                PackageHit("vlc", "", "player"), PackageHit("bashtop", "", "x")]

    def installed_packages(self):
        self.calls += 1
        return {"vlc": "3.0"}

    def info_text(self, pkg):
        return "info for " + pkg


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeBackend()
        self.model = TuiModel(self.backend,
                              Database(pathlib.Path(tempfile.mkdtemp()) / "t.db"))

    def test_ranking(self):
        self.assertEqual([rank("vlc", n) for n in ("vlc", "vlc-bin", "libvlc", "other")],
                         [0, 1, 2, 3])

    def test_search_sorts_and_marks_installed(self):
        hits = self.model.search("vlc")
        self.assertEqual([h.name for h in hits], ["vlc", "vlc-bin", "libvlc", "bashtop"])
        self.assertTrue(hits[0].installed)
        self.assertEqual(hits[0].version, "3.0")
        self.assertFalse(hits[1].installed)

    def test_installed_is_cached_until_invalidated(self):
        self.model.installed()
        self.model.installed()
        self.assertEqual(self.backend.calls, 1)
        self.model.invalidate()
        self.model.installed()
        self.assertEqual(self.backend.calls, 2)

    def test_empty_query(self):
        self.assertEqual(self.model.search("  "), [])

    def test_aliases(self):
        self.assertTrue(self.model.add_alias("web", "nginx htop"))
        self.assertFalse(self.model.add_alias("bad;name", "x"))
        self.assertFalse(self.model.add_alias("ok", ""))
        rows = self.model.alias_rows()
        self.assertIn(("web", "nginx htop", "custom"), rows)
        self.assertTrue(any(kind == "builtin" for *_, kind in rows))
        self.assertTrue(self.model.remove_alias("web"))

    def test_system_info_keys_have_translations(self):
        for lang in i18n.SUPPORTED:
            cat = i18n.catalog(lang)
            for key, _ in self.model.system_info():
                self.assertIn("tui_sys_" + key, cat)
            for kind in ("builtin", "custom"):
                self.assertIn("tui_alias_type_" + kind, cat)


class DepsTests(unittest.TestCase):
    def test_activate_uses_private_venv(self):
        home = tempfile.mkdtemp()
        sp = pathlib.Path(home, ".local/share/dpa/tui-venv/lib/python%d.%d/site-packages"
                          % sys.version_info[:2])
        (sp / "textual").mkdir(parents=True)
        (sp / "textual" / "__init__.py").write_text("MARK = 1\n")
        code = textwrap.dedent("""
            import sys; sys.path.insert(0, %r)
            from dpa.tui import deps
            assert not deps.textual_available()
            assert deps.activate()
            import textual; assert textual.MARK == 1
            print("ok")
        """ % str(ROOT))
        env = dict(os.environ, HOME=home)
        env.pop("SUDO_USER", None)
        proc = subprocess.run([sys.executable, "-c", code], env=env,
                              capture_output=True, text=True)
        self.assertEqual(proc.stdout.strip(), "ok", proc.stderr)


class LaunchTests(unittest.TestCase):
    def setUp(self):
        OPTS.dry_run = OPTS.assume_yes = False
        self.backend = types.SimpleNamespace(name="apt")

    def tearDown(self):
        OPTS.dry_run = OPTS.assume_yes = False

    def test_declined_install_returns_false(self):
        with mock.patch.object(deps, "activate", return_value=False), \
                mock.patch("dpa.ui.confirm", return_value=False), \
                mock.patch.object(deps, "install") as inst:
            self.assertFalse(launch(self.backend, None))
            inst.assert_not_called()

    def test_failed_install_returns_false(self):
        with mock.patch.object(deps, "activate", return_value=False), \
                mock.patch("dpa.ui.confirm", return_value=True), \
                mock.patch.object(deps, "install", return_value=False):
            self.assertFalse(launch(self.backend, None))

    def test_install_only_with_deps_ready(self):
        with mock.patch.object(deps, "activate", return_value=True):
            self.assertTrue(launch(self.backend, None, install_only=True))

    def test_install_only_installs_without_asking(self):
        with mock.patch.object(deps, "activate", side_effect=[False, True]), \
                mock.patch("dpa.ui.confirm") as ask, \
                mock.patch.object(deps, "install", return_value=True):
            self.assertTrue(launch(self.backend, None, install_only=True))
            ask.assert_not_called()

    def test_requires_tty(self):
        with mock.patch.object(deps, "activate", return_value=True), \
                mock.patch("sys.stdin.isatty", return_value=False):
            self.assertFalse(launch(self.backend, None))

    def test_cli_works_without_textual_installed(self):
        # CLI не должен импортировать textual при старте
        self.assertNotIn("textual", sys.modules)


def _install_fake_textual():
    """Заглушки textual/rich: проверяем, что app.py импортируется и его
    классы создаются (опечатки, ключи переводов в теле классов)."""
    class Meta(type):
        def __getattr__(cls, name):
            if name.startswith("__"):
                raise AttributeError(name)
            return Meta(name, (Base,), {})

        def __getitem__(cls, item):
            return cls

    class Base(metaclass=Meta):
        def __init__(self, *a, **k):
            pass

    def deco(*a, **k):
        return lambda f: f

    spec = {
        "textual": {"on": deco, "work": deco},
        "textual.app": {"App": Base, "ComposeResult": Base},
        "textual.binding": {"Binding": Base},
        "textual.containers": {"Horizontal": Base, "Vertical": Base, "VerticalScroll": Base},
        "textual.screen": {"ModalScreen": Base},
        "textual.widgets": {n: Base for n in (
            "Button", "DataTable", "Footer", "Header", "Input", "Label", "Static",
            "TabbedContent", "TabPane")},
        "rich": {}, "rich.markup": {"escape": lambda text: text}, "rich.table": {"Table": Base}, "rich.text": {"Text": Base},
    }
    saved = {}
    for name, attrs in spec.items():
        saved[name] = sys.modules.get(name)
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        sys.modules[name] = mod
    return saved


class FakeTextualImportTests(unittest.TestCase):
    def test_app_module_imports_and_defines_classes(self):
        saved = _install_fake_textual()
        sys.modules.pop("dpa.tui.app", None)
        try:
            app = importlib.import_module("dpa.tui.app")
            for name in ("DpaApp", "PackagesPanel", "InstalledPanel", "SystemPanel",
                         "HistoryPanel", "AliasesPanel", "SettingsPanel",
                         "ConfirmScreen", "run_app"):
                self.assertTrue(hasattr(app, name), name)
        finally:
            sys.modules.pop("dpa.tui.app", None)
            for name, mod in saved.items():
                if mod is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = mod


def _have_textual():
    import importlib.util
    return importlib.util.find_spec("textual") is not None


class FakeModel:
    pm = "apt"

    def search(self, q):
        return [PackageHit("vlc", "3.0", "player", True),
                PackageHit("htop", "", "monitor", False)]

    def info(self, n):
        return "info " + n

    def installed(self, refresh=False):
        return {"vlc": "3.0"}

    def invalidate(self):
        pass

    def system_info(self):
        return [("distribution", "Test OS"), ("pm", "APT")]

    def history(self, limit=200):
        return []

    def alias_rows(self):
        return [("docker", "docker.io", "builtin")]

    def add_alias(self, a, t):
        return True

    def remove_alias(self, a):
        return True


@unittest.skipUnless(_have_textual(), "Textual не установлен (dpa tui --install-deps)")
class RealTextualTests(unittest.IsolatedAsyncioTestCase):
    """Запускаются только у тех, у кого стоит Textual."""

    async def test_search_mark_and_confirm_dialog(self):
        from dpa.tui.app import ConfirmScreen, DpaApp
        service = mock.Mock()
        app = DpaApp(FakeModel(), service)
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            app.query_one("#pkg-query").value = "vlc"
            await pilot.click("#pkg-search")
            await app.workers.wait_for_complete()
            await pilot.pause()
            table = app.query_one("#pkg-table")
            self.assertEqual(table.row_count, 2)
            table.focus()
            await pilot.press("down")
            await pilot.press("i")  # htop не установлен -> диалог подтверждения
            await pilot.pause()
            self.assertIsInstance(app.screen, ConfirmScreen)
            await pilot.press("escape")
            await pilot.pause()
            service.install.assert_not_called()

    async def test_tabs_by_click_and_keys(self):
        from dpa.tui.app import DpaApp
        from textual.widgets import TabbedContent
        app = DpaApp(FakeModel(), mock.Mock())
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            tabs = app.query_one(TabbedContent)
            self.assertEqual(tabs.active, "tab-packages")
            app.query_one("#pkg-table").focus()
            await pilot.press("3")
            await pilot.pause()
            self.assertEqual(tabs.active, "tab-system")


if __name__ == "__main__":
    unittest.main()
