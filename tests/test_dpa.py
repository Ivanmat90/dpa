import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dpa import aliases, cli, completions, config, i18n  # noqa: E402
from dpa.arch import common, gpu, server  # noqa: E402
from dpa.backends import apt, detect_name, dnf, pacman, parse_os_release  # noqa: E402
from dpa.db import Database  # noqa: E402
from dpa.options import OPTS  # noqa: E402


class I18nTests(unittest.TestCase):
    def test_catalogs_have_same_keys(self):
        self.assertEqual(set(i18n.catalog("en")), set(i18n.catalog("ru")))

    def test_every_used_key_exists(self):
        used = set()
        for path in (ROOT / "dpa").rglob("*.py"):
            if "locales" in path.parts:
                continue
            used |= set(re.findall(r'\bt\(\s*"([a-z0-9_]+)"\s*[,)]', path.read_text(encoding="utf-8")))
        used |= {c[3] for c in cli.COMMANDS} | {c[0] for c in cli.COMMANDS}
        self.assertEqual(sorted(used - set(i18n.catalog("en"))), [])

    def test_placeholders_match(self):
        for key, en in i18n.catalog("en").items():
            ru = i18n.catalog("ru")[key]
            self.assertEqual(en.count("{}"), ru.count("{}"), key)


class BackendTests(unittest.TestCase):
    def test_apt(self):
        b = apt.AptBackend()
        self.assertEqual(b.cmd_install(["vlc"], True), ["apt", "install", "-y", "vlc"])
        self.assertEqual(b.cmd_install(["vlc"], False), ["apt", "install", "vlc"])

    def test_dnf_and_pacman(self):
        self.assertEqual(dnf.DnfBackend().cmd_remove(["x"], True), ["dnf", "remove", "-y", "x"])
        self.assertEqual(pacman.PacmanBackend().cmd_upgrade(True), ["pacman", "-Syu", "--noconfirm"])
        self.assertEqual(pacman.PacmanBackend().cmd_install(["x"], False), ["pacman", "-S", "--needed", "x"])

    def test_detect_from_os_release(self):
        with tempfile.NamedTemporaryFile("w", suffix=".rel", delete=False) as fh:
            fh.write('ID=manjaro\nID_LIKE=arch\nPRETTY_NAME="Manjaro"\n')
        self.assertEqual(parse_os_release(fh.name)["ID"], "manjaro")
        with mock.patch("dpa.backends.which", return_value="/usr/bin/pacman"), \
                mock.patch.dict(os.environ, {"DPA_BACKEND": ""}):
            self.assertEqual(detect_name(fh.name), "pacman")


class AliasTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(pathlib.Path(tempfile.mkdtemp()) / "t.db")

    def test_builtin_per_distro(self):
        self.assertEqual(aliases.resolve(["docker"], "apt", self.db, False), ["docker.io"])
        self.assertEqual(aliases.resolve(["build-essential"], "dnf", self.db, False),
                         ["gcc", "gcc-c++", "make"])
        self.assertEqual(aliases.resolve(["htop"], "pacman", self.db, False), ["htop"])

    def test_custom_overrides_builtin(self):
        self.db.add_alias("docker", "podman", "apt")
        self.assertEqual(aliases.resolve(["docker"], "apt", self.db, False), ["podman"])
        self.assertTrue(self.db.remove_alias("docker", "apt"))
        self.assertFalse(self.db.remove_alias("docker", "apt"))

    def test_name_validation(self):
        self.assertTrue(aliases.valid_name("libstdc++6"))
        for bad in ("-rf", "a;b", "a b", "$(x)"):
            self.assertFalse(aliases.valid_name(bad), bad)

    def test_history(self):
        self.db.log("install", ["vlc"], "success")
        self.assertEqual(self.db.history(5)[0]["packages"], ["vlc"])


class ArchTests(unittest.TestCase):
    def test_multilib_enable_is_idempotent(self):
        text = "[options]\n\n#[multilib]\n#Include = /etc/pacman.d/mirrorlist\n"
        new, changed = common.enable_multilib_text(text)
        self.assertTrue(changed)
        self.assertIn("[multilib]\nInclude = /etc/pacman.d/mirrorlist", new)
        self.assertFalse(common.enable_multilib_text(new)[1])

    def test_gpu_parsing(self):
        out = ("01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP106 [GeForce GTX 1060]\n"
               "00:02.0 VGA compatible controller [0300]: Intel Corporation UHD Graphics\n"
               "02:00.0 Ethernet controller: Intel Corporation I219\n")
        gpus = gpu.parse_lspci(out)
        self.assertEqual([g.vendor for g in gpus], ["nvidia", "intel"])
        self.assertTrue(gpus[0].legacy_nvidia)
        self.assertNotIn("nvidia-open", gpus[0].packages)
        rtx = gpu.parse_lspci("VGA compatible controller: NVIDIA Corporation [GeForce RTX 3070]")
        self.assertIn("nvidia-open", rtx[0].packages)

    def test_virtualbox_does_not_get_vmware_driver(self):
        g = gpu.parse_lspci("00:02.0 VGA compatible controller: InnoTek Systems VirtualBox Graphics Adapter")
        self.assertEqual(g[0].packages, ["virtualbox-guest-utils"])

    def test_mkinitcpio_modules_merge(self):
        out = gpu._mkinit_modules("MODULES=(btrfs)\nHOOKS=(base)\n")
        self.assertIn("MODULES=(btrfs nvidia nvidia_modeset nvidia_uvm nvidia_drm)", out)

    def test_server_selection_by_number_and_name(self):
        self.assertEqual(server.parse_selection(["1", "database"]), ["web", "database"])

    def test_every_server_package_has_known_category(self):
        for pkgs in server.CATEGORIES.values():
            self.assertTrue(pkgs)


class TargetTests(unittest.TestCase):
    def test_auto_target_installed_system(self):
        with mock.patch("os.path.ismount", return_value=False), \
                mock.patch("os.path.isdir", return_value=False):
            self.assertEqual(common.auto_target(), "/")

    def test_auto_target_when_mnt_is_mounted(self):
        with mock.patch("os.path.ismount", return_value=True):
            self.assertEqual(common.auto_target(), "/mnt")

    def test_auto_target_on_live_iso_never_picks_running_system(self):
        with mock.patch("os.path.ismount", return_value=False), \
                mock.patch("os.path.isdir", side_effect=lambda p: p == "/run/archiso"):
            self.assertEqual(common.auto_target(), "/mnt")

    def test_arch_install_refuses_running_system(self):
        from dpa.arch.install import run_arch_install
        self.assertFalse(run_arch_install("pacman", "/", []))

    def test_host_target_skips_mount_and_base_checks(self):
        with mock.patch("dpa.arch.common.is_root", return_value=True), \
                mock.patch("dpa.arch.common.which", return_value="/usr/bin/pacman"):
            self.assertTrue(common.preflight("pacman", "/", "arch-desktop"))

    def test_desktop_on_installed_system_uses_host_without_target_flag(self):
        env = {"HOME": tempfile.mkdtemp(), "DPA_BACKEND": "pacman", "DPA_LANG": "en"}
        with mock.patch.dict(os.environ, env), \
                mock.patch("dpa.arch.common.auto_target", return_value="/"), \
                mock.patch("dpa.arch.common.is_root", return_value=True), \
                mock.patch("dpa.arch.common.which", return_value="/usr/bin/pacman"), \
                mock.patch("dpa.arch.common.chroot_run") as chroot:
            chroot.return_value = mock.Mock(ok=True)
            self.assertEqual(cli.main(["arch-desktop", "--de", "xfce", "--no-gpu"]), 0)
            first = chroot.call_args_list[0]
            self.assertEqual(first[0][0], "/")
            self.assertIn("xfce4", first[0][1])
        OPTS.dry_run = OPTS.assume_yes = False


class CompletionTests(unittest.TestCase):
    def test_bash_is_valid_and_complete(self):
        script = completions.bash(cli.build_parser())
        for name, *_ in [(c[1],) for c in cli.COMMANDS]:
            self.assertIn(name, script)
        proc = subprocess.run(["bash", "-n"], input=script, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_all_shells_generate(self):
        for gen in completions.GENERATORS.values():
            self.assertIn("arch-desktop", gen(cli.build_parser()))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        env = {"HOME": self.home, "DPA_BACKEND": "apt", "DPA_LANG": "en"}
        self.patch = mock.patch.dict(os.environ, env)
        self.patch.start()
        OPTS.dry_run = OPTS.assume_yes = False

    def tearDown(self):
        self.patch.stop()
        i18n.set_language("en")
        OPTS.dry_run = OPTS.assume_yes = False

    def test_dry_run_install_succeeds_and_is_not_logged(self):
        self.assertEqual(cli.main(["install", "--dry-run", "vlc"]), 0)
        self.assertEqual(Database().history(), [])

    def test_failed_command_gives_nonzero_exit(self):
        with mock.patch("dpa.backends.base.run") as run:
            run.return_value = mock.Mock(ok=False)
            self.assertEqual(cli.main(["install", "-y", "vlc"]), 1)
        self.assertEqual(Database().history()[0]["status"], "failed")

    def test_invalid_package_rejected(self):
        self.assertEqual(cli.main(["install", "a;b"]), 1)

    def test_alias_roundtrip(self):
        self.assertEqual(cli.main(["alias", "add", "x", "htop"]), 0)
        self.assertEqual(cli.main(["alias", "remove", "x"]), 0)
        self.assertEqual(cli.main(["alias", "remove", "x"]), 1)

    def test_command_short_forms(self):
        self.assertEqual(cli.main(["i", "--dry-run", "vlc"]), 0)
        self.assertEqual(cli.main(["rm", "--dry-run", "vlc"]), 0)

    def test_lang_switch_persists(self):
        self.assertEqual(cli.main(["lang", "ru"]), 0)
        self.assertEqual(config.resolve_language(), "en" if os.environ.get("DPA_LANG") else "ru")
        del os.environ["DPA_LANG"]
        self.assertEqual(config.resolve_language(), "ru")

    def test_arch_commands_dry_run_on_pacman(self):
        with mock.patch.dict(os.environ, {"DPA_BACKEND": "pacman"}):
            for argv in (["arch-install"], ["arch-desktop", "--de", "kde"],
                         ["arch-dev"], ["arch-gaming"],
                         ["arch-server", "--services", "web", "database"]):
                self.assertEqual(cli.main(argv + ["--dry-run"]), 0, argv)

    def test_arch_refuses_without_dry_run_when_not_root_or_mounted(self):
        with mock.patch.dict(os.environ, {"DPA_BACKEND": "apt"}):
            self.assertEqual(cli.main(["arch-install"]), 1)


if __name__ == "__main__":
    unittest.main()
