# DPA - Dnf Pacman Apt

A unified interface for `apt`, `dnf`, and `pacman`: use the same commands across Debian/Ubuntu, Fedora/RHEL, and Arch. No external dependencies required—only Python 3.8+ is needed.

```
dpa install vlc          # install a package
dpa upgrade              # upgrade the system
dpa search python        # search for a package
dpa install --dry-run docker   # show what will be done, without making any changes
```

## Installation

```bash
git clone https://github.com/Ivanmat90/dpa.git
cd dpa
./install-dpa.sh            # prompts for language; or use: ./install-dpa.sh --lang ru
```

The installer bundles the `dpa/` package into a single executable file at `/usr/local/bin/dpa`, sets the language, and installs shell autocompletion (for bash, zsh, or fish).
To install without cloning the repository: `curl -fsSL https://raw.githubusercontent.com/Ivanmat90/dpa/main/install-dpa.sh | bash`

Uninstallation: `dpa uninstall` (use `--keep-data` to preserve your history and aliases).

## Commands

| Command | Description |
|---|---|
| `install` (`i`, `add`) / `remove` (`rm`) | install / remove packages |
| `update` / `upgrade` (`up`) | update package metadata / upgrade the system |
| `search` (`s`), `info` (`show`), `list` (`ls`) | search, view info, or list packages (`dpa ls python` — supports filtering) |
| `clean`, `autoremove` | clear cache / remove unnecessary packages |
| `history` (`log`) | view history (use `-n 50` to specify the number of entries) |
| `alias add|list|remove` | custom package names (e.g., `dpa alias add web nginx`) |
| `tui` | interactive interface with mouse support (optional; see below) |
| `distro`, `lang [en|ru]`, `completion` | system, language, shell autocompletion |
| `arch-install`, `arch-config`, `arch-desktop`, `arch-server`, `arch-dev`, `arch-gaming` | Arch Linux installation and configuration |

General flags (can be used before or after the command): `-y/--yes`, `--dry-run`, `--no-color`.
Without `-y`, the package manager will prompt you, allowing you to review the full list of changes.
Language: set via `dpa lang ru` or the `DPA_LANG` environment variable. The `DPA_BACKEND=apt|dnf|pacman`
variable forces the use of a specific backend (useful for testing with `--dry-run`).

## TUI – Interactive Interface (Optional)

```bash
dpa tui                     # launch; if a required library is missing, it will offer to install it
dpa tui --install-deps      # install only the dependencies (alternatively, use ./install-dpa.sh --with-tui)
```

The standard CLI operates without any third-party libraries. The TUI is built on
[Textual](https://textual.textualize.io/) and is installed **separately**: `dpa` creates a private
virtual environment at `~/.local/share/dpa/tui-venv` (no root access required; the system Python
remains untouched; an internet connection is necessary). If Textual is already present on your system, it will be used instead. Tabs: **Packages** (search, mark, install, and remove), **Installed** (filter),
**System** (update/upgrade/clean/autoremove), **History**, **Aliases**, **Settings** (language).
Mouse support: click on tabs, buttons, and rows; use the scroll wheel.

| Key | Action |
|---|---|
| `/` | go to search |
| `Enter` (in search) | perform search |
| `Space` / `i` / `r` (in table) | mark / install / remove |
| `1`–`6` | switch tabs |
| `F5` | refresh data |
| `Ctrl+P` | Textual command palette (includes theme switching) |
| `q`, `Ctrl+Q` | exit |

Operations that modify the system are executed **in the standard terminal**: the TUI temporarily yields the screen, allowing for `sudo` password prompts and interactive queries from `apt`/`dnf`/`pacman`; afterwards, you return to the TUI. Running `dpa --dry-run tui` will show what actions would be performed without making any actual changes.
Language changes in the settings take effect after restarting the TUI. ### Installing Arch Linux from a live ISO

```bash
# Partition disks, mount the root partition to /mnt (and the ESP to /mnt/boot or /mnt/boot/efi)
sudo dpa arch-install                 # pacstrap + fstab + NetworkManager
sudo dpa arch-config                  # locale, time zone, hostname, passwords, user, GRUB
sudo dpa arch-desktop --de kde        # desktop environment + graphics drivers
sudo dpa arch-dev --user ivan         # developer tools (+yay for the specified user)
umount -R /mnt && reboot
```

All `arch-*` commands support the `--target` option (which defaults to `/mnt`) and can be run directly from the live ISO;
there is no need to use `arch-chroot` manually. It is recommended to try them with the `--dry-run` flag first. ## Project Structure

```
dpa/
├── install-dpa.sh          installer (builds a zipapp, sets up autocompletion)
├── pyproject.toml          metadata (use `pip install -e .` for development)
├── tests/                  run with `python3 -m unittest discover -s tests`
│   ├── test_dpa.py         core functionality, backends, Arch support, autocompletion
│   └── test_tui.py         TUI (tests run against an actual Textual installation, if present)
└── dpa/                    package
├── cli.py              argument parsing, command table, dispatcher
├── manager.py          package operations (headers, history, timestamps)
├── backends/           apt.py, dnf.py, pacman.py + auto-detection
├── aliases.py, db.py   cross-distribution package name mapping, SQLite
├── ui.py               colors, icons, tables, banner, user prompts
├── i18n.py, locales/   translations: en.py, ru.py
├── runtime.py          command execution: sudo, --dry-run, error handling
├── config.py           configuration
```
