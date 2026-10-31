# DPA - Dnf Pacman Apt

**English** | [Русский](README-RU.md)

One command-line interface for `apt`, `dnf` and `pacman`: the same commands on
Debian/Ubuntu, Fedora/RHEL and Arch. No external dependencies, only Python 3.8+ is required.
An optional mouse-friendly TUI is available as well.

```
dpa install vlc                # install a package
dpa upgrade                    # upgrade the system
dpa search python              # search packages
dpa install --dry-run docker   # show what would be executed without changing anything
dpa tui                        # interactive interface (optional)
```

## Installation

```bash
git clone https://github.com/Ivanmat90/dpa.git
cd dpa
./install-dpa.sh                          # asks for the language and about the optional TUI
./install-dpa.sh --lang en --with-tui     # no questions (or --no-tui)
```

The installer builds the `dpa/` package into a single executable, `/usr/local/bin/dpa`,
sets the language and installs shell completion (bash/zsh/fish).
Without cloning: `curl -fsSL https://raw.githubusercontent.com/Ivanmat90/dpa/main/install-dpa.sh | bash`

Uninstall: `dpa uninstall` (`--keep-data` keeps the history and aliases).

## Commands

| Command | What it does |
|---|---|
| `install` (`i`, `add`) / `remove` (`rm`) | install / remove packages |
| `update` / `upgrade` (`up`) | refresh package information / upgrade the system |
| `search` (`s`), `info` (`show`), `list` (`ls`) | search, show details, list installed (`dpa ls python` filters the list) |
| `clean`, `autoremove` | clean the package cache / remove unused packages |
| `history` (`log`) | transaction history (`-n 50` sets the number of entries) |
| `alias add\|list\|remove` | your own package names (`dpa alias add web nginx`) |
| `tui` | interactive interface with mouse support (optional, see below) |
| `distro`, `lang [en\|ru]`, `completion` | system info, language, shell completion |
| `arch-install`, `arch-config`, `arch-desktop`, `arch-server`, `arch-dev`, `arch-gaming` | install and configure Arch Linux |

Global flags (work before and after the command): `-y/--yes`, `--dry-run`, `--no-color`.
Without `-y` the package manager itself asks the questions, so you always see the full list of changes.
Language: `dpa lang en` or the `DPA_LANG` environment variable. `DPA_BACKEND=apt|dnf|pacman`
forces a backend (handy for testing with `--dry-run`).

## TUI - interactive interface (optional)

```bash
dpa tui                     # start; offers to install the required library if it is missing
dpa tui --install-deps      # only install the dependency (or ./install-dpa.sh --with-tui)
```

The regular CLI works without any third-party libraries. The TUI is built on
[Textual](https://textual.textualize.io/) and is installed **separately**: dpa creates a private
virtual environment at `~/.local/share/dpa/tui-venv` (no root needed, the system Python stays
untouched, internet access is required). If Textual is already installed system-wide, it is used instead.

Tabs: **Packages** (search, marking, install and remove), **Installed** (with a filter),
**System** (update/upgrade/clean/autoremove), **History**, **Aliases**, **Settings** (language).
The mouse works: click tabs, buttons and rows, scroll with the wheel.

| Key | Action |
|---|---|
| `/` | go to search |
| `Enter` in the search box | search |
| `Space` / `i` / `r` in the table | mark / install / remove |
| `1`-`6` | switch tabs |
| `F5` | refresh data |
| `Ctrl+P` | Textual command palette (including theme switching) |
| `q`, `Ctrl+Q` | quit |

Operations that change the system run **in the regular terminal**: the TUI temporarily gives the
screen back, so the sudo password prompt and the apt/dnf/pacman questions work as usual; afterwards you
return to the TUI. `dpa --dry-run tui` shows what would be executed without changing anything.
A language change in Settings takes effect after the TUI is restarted.

### Installing Arch Linux from the live ISO

```bash
# partition the disks, mount the root to /mnt (and the ESP to /mnt/boot or /mnt/boot/efi)
sudo dpa arch-install                 # pacstrap + fstab + NetworkManager
sudo dpa arch-config                  # locale, time zone, hostname, passwords, user, GRUB
sudo dpa arch-desktop --de kde        # desktop environment + GPU drivers
sudo dpa arch-dev --user ivan         # developer tools (+ yay for the user)
umount -R /mnt && reboot
```

All `arch-*` commands work with `--target` (default `/mnt`) straight from the live ISO,
so there is no need to run `arch-chroot` manually. Try them with `--dry-run` first.

## Project structure

```
dpa/
├── install-dpa.sh          installer (builds a zipapp, installs completion)
├── pyproject.toml          metadata (pip install -e . for development)
├── tests/                  python3 -m unittest discover -s tests
│   ├── test_dpa.py         core, backends, Arch, completion
│   └── test_tui.py         TUI (tests against real Textual run if it is installed)
└── dpa/                    the package
    ├── cli.py              argument parsing, command table, dispatcher
    ├── manager.py          package operations (headers, history, timing)
    ├── backends/           apt.py, dnf.py, pacman.py + auto-detection
    ├── aliases.py, db.py   cross-distro package names, SQLite
    ├── ui.py               colours, icons, tables, banner, prompts
    ├── i18n.py, locales/   translations: en.py, ru.py
    ├── runtime.py          running commands: sudo, --dry-run, errors
    ├── config.py           paths and config (works correctly under sudo)
    ├── completions.py      bash/zsh/fish generated from the argparse parser
    ├── selfmanage.py       completion setup and uninstall
    ├── tui/                optional interface
    │   ├── __init__.py     launcher, offers to install Textual (does not need Textual itself)
    │   ├── deps.py         private venv with Textual
    │   ├── model.py        TUI data (search, aliases, history), no Textual
    │   └── app.py          the Textual interface itself (imported only on launch)
    └── arch/               common, gpu, install, configure, desktop, server, dev, gaming
```

### How to extend

* **New distribution / package manager** - one file in `dpa/backends/` (a class with `cmd_*` methods)
  and a line in `BACKENDS`.
* **New command** - an entry in `COMMANDS` (`cli.py`) and a handler in `dispatch`.
  Help and shell completion update themselves.
* **New TUI tab** - a panel class and a `TabPane` in `dpa/tui/app.py`, data - a method in `tui/model.py`.
* **New language** - `dpa/locales/<code>.py` and the code in `SUPPORTED` (`i18n.py`);
  a test makes sure the keys match.
* **New alias** - an entry in `BUILTIN` (`aliases.py`); list only the differences.
