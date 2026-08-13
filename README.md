# ⚡ DPA — Dnf Pacman Apt

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/dpa-team/dpa)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/dpa-team/dpa)](https://github.com/dpa-team/dpa/stargazers)

> **Universal Package Manager for Linux**  
> One syntax for all package managers. Simplicity for everyone.

---

## 🎯 Why DPA?

Tired of remembering different package manager commands?

```bash
# Ubuntu, Debian, Mint
sudo apt install vlc

# Fedora, RHEL
sudo dnf install vlc

# Arch, Manjaro
sudo pacman -S vlc
```

**With DPA, it's just:**

```bash
dpa install vlc
# Works on ALL distros!
```

---

## ✨ Features

- **One syntax** — `dpa install` works everywhere
- **Arch Installer** — Install Arch in 2 commands
- **Gaming Preset** — Steam, Lutris, Wine, Gamemode ready
- **Auto GPU Drivers** — Detects NVIDIA/AMD/Intel automatically
- **Multi-language** — English and Russian support
- **Transaction History** — All actions logged in SQLite
- **Clean Uninstall** — Removes itself without trace

---

## 🚀 Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/dpa-team/dpa/main/install-dpa.sh | bash
```

Or with wget:

```bash
wget -qO- https://raw.githubusercontent.com/dpa-team/dpa/main/install-dpa.sh | bash
```

---

## 📖 Usage Examples

### Basic Commands

```bash
dpa install vlc          # Install a package
dpa remove vlc           # Remove a package
dpa update               # Update package list
dpa upgrade              # Upgrade system
dpa search python        # Search for packages
dpa info vlc             # Show package info
dpa list                 # List installed packages
dpa clean                # Clean package cache
dpa autoremove           # Remove unused packages
dpa history              # Show transaction history
dpa distro               # Show system info
```

### Arch Linux Installation

```bash
sudo dpa arch-install              # Base installation
sudo dpa arch-desktop --de kde     # Install with KDE
sudo dpa arch-gaming                # Gaming environment
sudo dpa arch-dev                   # Development environment
sudo dpa arch-server                # Server environment
sudo dpa arch-config                # Interactive configuration
```

---

## 🎮 Gaming Preset

The `dpa arch-gaming` command installs:

- **Steam** — Main gaming client
- **Lutris** — All game launchers in one place
- **Wine** — Run Windows games
- **Gamemode** — Auto performance optimization
- **MangoHud** — FPS monitoring overlay
- **GOverlay** — GUI for MangoHud
- **VkBasalt** — Post-processing effects
- **Proton GE** — Custom Proton from GloriousEggroll
- **Discord** — Voice chat for gaming
- **OBS Studio** — Recording/streaming
- **FFmpeg** — Video codecs

---

## 🖥️ Auto GPU Drivers

DPA automatically detects your GPU and installs the right drivers:

| GPU | Driver |
|-----|--------|
| NVIDIA RTX 2000+ | `nvidia-open` |
| NVIDIA GTX 1000/1600 | `nvidia` |
| AMD RX 5000/6000/7000 | `mesa` + `amdgpu` |
| Intel | `mesa` + `xf86-video-intel` |
| VMware/VirtualBox | `xf86-video-vmware` |

---

## 🐚 Shell Support

DPA supports autocompletion in:

- **Bash** — `~/.bash_completion_dpa`
- **ZSH** — `~/.zsh_completion_dpa`
- **Fish** — `~/.config/fish/completions/dpa.fish`

---

## 🌍 Multi-Language Support

DPA speaks your language:

- English
- Русский

Select language during installation or change in `~/.config/dpa/config.json`

---

## 📦 Requirements

- Python 3.6+
- sudo privileges (for installation)
- Internet connection (for first run)

---

## 🗑️ Uninstall

```bash
dpa uninstall
```

This removes all DPA files, configs, and cache.

---

## ❤️ Support the Project

DPA is a free and open-source project created by a 15-year-old Linux enthusiast. If you find it useful, consider supporting:

- **Star** the project on GitHub
- **Report issues** and suggest features
- **Contribute code** and improvements
- **Donate** (optional) — links in the repo

---

## 📄 License

MIT License — free for everyone!

---

## 🙏 Acknowledgments

- Created by a 15-year-old developer who wanted to make Linux simpler
- Inspired by the chaos of different package manager syntaxes
- Built with love and vibecoding

---

**Made with ❤️ for the Linux community**

[![GitHub](https://img.shields.io/badge/GitHub-dpa--team/dpa-181717)](https://github.com/dpa-team/dpa)
