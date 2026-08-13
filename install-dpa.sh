#!/bin/bash
# install-dpa.sh - Самодостаточный инсталлятор DPA
# Версия: 2.0.0
# GitHub: https://github.com/dpa-team/dpa

set -e

# ============ ЦВЕТА ============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# ============ ПЕРЕМЕННЫЕ ============
DPA_VERSION="2.0.0"
INSTALL_DIR="/usr/local/bin"
DPA_BIN="dpa"
CONFIG_DIR="$HOME/.config/dpa"
CONFIG_FILE="$CONFIG_DIR/config.json"

# ============ ВЫБОР ЯЗЫКА ============
select_language() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     DPA INSTALLER                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Select language / Выберите язык:"
    echo ""
    echo "  1) English"
    echo "  2) Русский"
    echo ""
    read -p "Enter your choice / Введите номер (1-2): " lang_choice

    case $lang_choice in
        1|en|English|english|ENG|eng)
            LANG_CODE="en"
            LANG_NAME="English"
            ;;
        2|ru|Русский|русский|RUS|rus)
            LANG_CODE="ru"
            LANG_NAME="Русский"
            ;;
        *)
            echo "Invalid choice / Неверный выбор. Using English / Использую английский."
            LANG_CODE="en"
            LANG_NAME="English"
            ;;
    esac

    echo ""
    echo -e "${GREEN}Language set to: ${LANG_NAME}${NC}"
    echo ""
    sleep 1
}

# ============ ПЕРЕМЕННЫЕ ДЛЯ СООБЩЕНИЙ ============
if [ "$LANG_CODE" = "ru" ]; then
    MSG_BANNER="Универсальный менеджер пакетов"
    MSG_INSTALLING="Установка DPA..."
    MSG_CHECKING="Проверка системы..."
    MSG_PYTHON="Python 3 не найден!"
    MSG_INSTALL_PYTHON="Установите Python 3:"
    MSG_SUDO="Нет прав sudo!"
    MSG_DIRS="Создание директорий..."
    MSG_DIRS_OK="Директории созданы"
    MSG_CREATING="Создание DPA..."
    MSG_COMPLETION="Настройка автодополнения..."
    MSG_BASH="Автодополнение для bash добавлено"
    MSG_FISH="Автодополнение для fish добавлено"
    MSG_ZSH="Автодополнение для zsh добавлено"
    MSG_TESTING="Тестирование DPA..."
    MSG_WORKS="DPA работает!"
    MSG_INSTALLED="DPA успешно установлен!"
    MSG_MAIN="Основные команды:"
    MSG_ARCH="Команды Arch Linux (только в Arch):"
    MSG_ALIAS="Управление алиасами:"
    MSG_SHELL="Поддержка оболочек:"
    MSG_RELOAD="Перезагрузите терминал: source ~/.bashrc"
    MSG_ERROR="Ошибка: установка не удалась!"
    MSG_LANG="Язык установлен"
else
    MSG_BANNER="Universal Package Manager"
    MSG_INSTALLING="Installing DPA..."
    MSG_CHECKING="Checking system..."
    MSG_PYTHON="Python 3 not found!"
    MSG_INSTALL_PYTHON="Install Python 3:"
    MSG_SUDO="No sudo privileges!"
    MSG_DIRS="Creating directories..."
    MSG_DIRS_OK="Directories created"
    MSG_CREATING="Creating DPA..."
    MSG_COMPLETION="Setting up shell completions..."
    MSG_BASH="Bash completion added"
    MSG_FISH="Fish completion added"
    MSG_ZSH="ZSH completion added"
    MSG_TESTING="Testing DPA..."
    MSG_WORKS="DPA works!"
    MSG_INSTALLED="DPA installed successfully!"
    MSG_MAIN="Main commands:"
    MSG_ARCH="Arch Linux commands (only in Arch):"
    MSG_ALIAS="Alias management:"
    MSG_SHELL="Shell support:"
    MSG_RELOAD="Reload your shell: source ~/.bashrc"
    MSG_ERROR="Error: Installation failed!"
    MSG_LANG="Language set to"
fi

# ============ БАННЕР ============
print_banner() {
    echo -e "${CYAN}"
    echo "  ██████╗ ██████╗  █████╗ "
    echo "  ██╔══██╗██╔══██╗██╔══██╗"
    echo "  ██║  ██║██████╔╝███████║"
    echo "  ██║  ██║██╔═══╝ ██╔══██║"
    echo "  ██████╔╝██║     ██║  ██║"
    echo "  ╚═════╝ ╚═╝     ╚═╝  ╚═╝"
    echo -e "${NC}"
    echo -e "${GREEN}  ${MSG_BANNER} v${DPA_VERSION}${NC}"
    echo -e "${YELLOW}  apt | dnf | pacman | zypper | yum${NC}"
    echo -e "${PURPLE}  https://github.com/dpa-team/dpa${NC}"
    echo ""
}

# ============ ВЕСЬ КОД DPA ВСТРОЕН (С ПОДДЕРЖКОЙ ЯЗЫКОВ) ============
create_dpa_script() {
    echo -e "${BLUE}${MSG_CREATING}${NC}"

    # Передаём язык в Python скрипт
    cat > /tmp/dpa.py << EOF
#!/usr/bin/env python3
"""
DPA - Dnf Pacman Apt v2.0.0
Universal Package Manager for Linux
"""

import os
import sys
import json
import subprocess
import argparse
import time
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

VERSION = "2.0.0"
LANG = "$LANG_CODE"  # Передаём язык из установщика

# ============ ПЕРЕВОДЫ ============
STRINGS = {
    'en': {
        # Messages
        'installing': "Installing: {}",
        'removing': "Removing: {}",
        'updating': "Updating package list",
        'upgrading': "Upgrading system",
        'searching': "Searching: {}",
        'info_pkg': "Package info: {}",
        'listing': "Listing installed packages",
        'cleaning': "Cleaning package cache",
        'autoremoving': "Removing unused packages",
        'completed': "Installation completed: {} package(s)",
        'removed': "Removal completed: {} package(s)",
        'updated': "Package list updated",
        'upgraded': "System upgraded",
        'cleaned': "Cache cleaned",
        'autoremoved': "Unused packages removed",
        'failed': "Operation failed",

        # History
        'history_title': "Transaction history (last {})",
        'history_empty': "History is empty",

        # Distro
        'distro_title': "System Information:",
        'distro_name': "  Distribution: {}",
        'distro_pm': "  Package Manager: {}",
        'distro_cache': "  Cache: {}",
        'distro_config': "  Config: {}",
        'distro_data': "  Data: {}",

        # Arch
        'arch_install_title': "Arch Linux Installation",
        'arch_install_base': "Installing base system...",
        'arch_install_fstab': "Generating fstab...",
        'arch_install_config': "Configuring system...",
        'arch_install_ok': "Arch Linux installed successfully",
        'arch_install_path': "  System installed to: {}",
        'arch_install_next': "Next steps:",
        'arch_install_step1': "  1. arch-chroot {}",
        'arch_install_step2': "  2. dpa arch-config  # Configure system",
        'arch_install_step3': "  3. Or install desktop: dpa arch-desktop --de gnome",

        'arch_config_title': "Arch Linux Configuration",
        'arch_config_not_arch': "This is not Arch Linux or not in chroot!",
        'arch_config_chroot': "Run after: arch-chroot /mnt",
        'arch_config_root': "Run with sudo: sudo dpa arch-config",
        'arch_config_locale': "Configuring locale...",
        'arch_config_hostname': "Setting hostname...",
        'arch_config_enter_host': "Enter hostname [archlinux]: ",
        'arch_config_root_pw': "Setting root password...",
        'arch_config_user': "Creating user...",
        'arch_config_create': "Create user? (y/N): ",
        'arch_config_username': "Username: ",
        'arch_config_set_pw': "Set password for {}",
        'arch_config_user_ok': "User {} created",
        'arch_config_boot': "Installing bootloader...",
        'arch_config_boot_mode': "UEFI or BIOS? (uefi/bios): ",
        'arch_config_disk': "Disk (e.g., /dev/sda): ",
        'arch_config_skip': "Skipping bootloader installation",
        'arch_config_ok': "Configuration completed",
        'arch_config_exit': "Exit chroot (exit) and reboot",

        'arch_desktop_title': "Installing {}",
        'arch_desktop_not_arch': "This is not Arch Linux!",
        'arch_desktop_root': "Run with sudo: sudo dpa arch-desktop",
        'arch_desktop_not_found': "Environment '{}' not found!",
        'arch_desktop_available': "Available environments:",
        'arch_desktop_example': "Example: dpa arch-desktop --de gnome",
        'arch_desktop_not_mount': "{} does not exist!",
        'arch_desktop_first': "First install base system: sudo dpa arch-install",
        'arch_desktop_packages': "Installing packages: {}",
        'arch_desktop_gpu': "Detecting and installing GPU drivers...",
        'arch_desktop_service': "Service {} enabled",
        'arch_desktop_ok': "{} installed",
        'arch_desktop_reboot': "Reboot and login to your system",
        'arch_desktop_pw': "Root password: root (change on first login)",

        'arch_server_title': "Arch Linux Server Environment",
        'arch_server_available': "Available services:",
        'arch_server_enter': "Enter services to install (space separated, or Enter for defaults):",
        'arch_server_default': "Default: web, database, devops",
        'arch_server_unknown': "Unknown service: {}",
        'arch_server_none': "No packages to install",
        'arch_server_install': "Installing: {}",
        'arch_server_ok': "Server environment installed",
        'arch_server_complete': "To complete setup:",

        'arch_dev_title': "Arch Linux Development Environment",
        'arch_dev_install': "Installing developer packages...",
        'arch_dev_aur': "Installing AUR helper (yay)...",
        'arch_dev_ok': "Development environment installed",
        'arch_dev_extra': "Additional steps:",
        'arch_dev_aur_pkgs': "  # Install additional AUR packages with yay",

        'arch_gaming_title': "Arch Linux Gaming Environment",
        'arch_gaming_install': "Installing gaming packages...",
        'arch_gaming_ok': "Gaming environment installed",
        'arch_gaming_list': "  Installed:",

        # GPU
        'gpu_detecting': "Detecting GPU...",
        'gpu_unknown': "Unable to detect GPU. Skipping drivers.",
        'gpu_detected': "  Detected: {}",
        'gpu_vendor': "  Vendor: {}",
        'gpu_driver': "  Recommended driver: {}",
        'gpu_no_packages': "No driver packages for {}. Skipping.",
        'gpu_installing': "Installing drivers: {}",
        'gpu_failed': "Failed to install drivers for {}",
        'gpu_ok': "Drivers for {} installed",
        'gpu_nvidia_config': "NVIDIA configuration created",
        'gpu_nvidia_mkinit': "NVIDIA added to mkinitcpio",

        # Errors
        'error_pm': "Unable to detect package manager!",
        'error_not_arch': "This is not Arch Linux!",
        'error_root': "Run with sudo: sudo dpa {}",
        'error_mount': "/mnt does not exist!",
        'error_mount_help': "Mount root partition first: mount /dev/sdX1 /mnt",
        'error_chroot': "Run after: arch-chroot /mnt",
        'error_pacstrap_removed': "Warning: 'dpa pacstrap' has been removed",
        'error_pacstrap_orig': "Use the original pacstrap command:",
        'error_pacstrap_cmd': "  sudo pacstrap /mnt base linux",
        'error_pacstrap_use': "Or use DPA's useful Arch commands:",

        # Status
        'status_ok': "[OK]",
        'status_fail': "[FAIL]",
        'status_warn': "[WARN]",
        'status_info': "[INFO]",

        # Alias
        'alias_added': "Alias added: {} -> {}",
        'alias_builtin': "Built-in aliases:",
        'alias_custom': "Custom aliases: (none)",
        'alias_add_help': "Add custom alias: dpa alias add --alias <name> --real <package>",

        # Uninstall
        'uninstalling': "Removing DPA...",
        'uninstalled': "DPA removed successfully",
        'uninstall_removed': "  Removed: {}",
        'uninstall_dir': "  Removed directory: {}",
        'uninstall_warn': "  Warning: Could not remove {}: {}",

        # Interrupt
        'interrupt': "\nInterrupted by user",
    },
    'ru': {
        # Messages
        'installing': "Установка: {}",
        'removing': "Удаление: {}",
        'updating': "Обновление списка пакетов",
        'upgrading': "Обновление системы",
        'searching': "Поиск: {}",
        'info_pkg': "Информация о пакете: {}",
        'listing': "Список установленных пакетов",
        'cleaning': "Очистка кеша пакетов",
        'autoremoving': "Удаление ненужных пакетов",
        'completed': "Установка завершена: {} пакет(ов)",
        'removed': "Удаление завершено: {} пакет(ов)",
        'updated': "Список пакетов обновлён",
        'upgraded': "Система обновлена",
        'cleaned': "Кеш очищен",
        'autoremoved': "Ненужные пакеты удалены",
        'failed': "Операция не удалась",

        # History
        'history_title': "История транзакций (последние {})",
        'history_empty': "История пуста",

        # Distro
        'distro_title': "Информация о системе:",
        'distro_name': "  Дистрибутив: {}",
        'distro_pm': "  Менеджер пакетов: {}",
        'distro_cache': "  Кеш: {}",
        'distro_config': "  Конфиг: {}",
        'distro_data': "  Данные: {}",

        # Arch
        'arch_install_title': "Установка Arch Linux",
        'arch_install_base': "Установка базовой системы...",
        'arch_install_fstab': "Генерация fstab...",
        'arch_install_config': "Настройка системы...",
        'arch_install_ok': "Arch Linux успешно установлен",
        'arch_install_path': "  Система установлена в: {}",
        'arch_install_next': "Следующие шаги:",
        'arch_install_step1': "  1. arch-chroot {}",
        'arch_install_step2': "  2. dpa arch-config  # Настройка системы",
        'arch_install_step3': "  3. Или установите DE: dpa arch-desktop --de gnome",

        'arch_config_title': "Настройка Arch Linux",
        'arch_config_not_arch': "Это не Arch Linux или не chroot!",
        'arch_config_chroot': "Запустите после: arch-chroot /mnt",
        'arch_config_root': "Запустите с sudo: sudo dpa arch-config",
        'arch_config_locale': "Настройка локалей...",
        'arch_config_hostname': "Настройка имени хоста...",
        'arch_config_enter_host': "Введите имя хоста [archlinux]: ",
        'arch_config_root_pw': "Настройка пароля root...",
        'arch_config_user': "Создание пользователя...",
        'arch_config_create': "Создать пользователя? (y/N): ",
        'arch_config_username': "Имя пользователя: ",
        'arch_config_set_pw': "Установите пароль для {}",
        'arch_config_user_ok': "Пользователь {} создан",
        'arch_config_boot': "Установка загрузчика...",
        'arch_config_boot_mode': "UEFI или BIOS? (uefi/bios): ",
        'arch_config_disk': "Диск (например, /dev/sda): ",
        'arch_config_skip': "Пропускаем установку загрузчика",
        'arch_config_ok': "Настройка завершена",
        'arch_config_exit': "Выйдите из chroot (exit) и перезагрузитесь",

        'arch_desktop_title': "Установка {}",
        'arch_desktop_not_arch': "Это не Arch Linux!",
        'arch_desktop_root': "Запустите с sudo: sudo dpa arch-desktop",
        'arch_desktop_not_found': "Окружение '{}' не найдено!",
        'arch_desktop_available': "Доступные окружения:",
        'arch_desktop_example': "Пример: dpa arch-desktop --de gnome",
        'arch_desktop_not_mount': "{} не существует!",
        'arch_desktop_first': "Сначала установите базовую систему: sudo dpa arch-install",
        'arch_desktop_packages': "Установка пакетов: {}",
        'arch_desktop_gpu': "Определение и установка драйверов для видеокарты...",
        'arch_desktop_service': "Сервис {} включён",
        'arch_desktop_ok': "{} установлен",
        'arch_desktop_reboot': "Перезагрузитесь и войдите в систему",
        'arch_desktop_pw': "Пароль root: root (измените при первом входе)",

        'arch_server_title': "Установка серверного окружения Arch Linux",
        'arch_server_available': "Доступные сервисы:",
        'arch_server_enter': "Введите сервисы через пробел (или Enter для стандартных):",
        'arch_server_default': "Стандартные: web, database, devops",
        'arch_server_unknown': "Неизвестный сервис: {}",
        'arch_server_none': "Нет пакетов для установки",
        'arch_server_install': "Установка: {}",
        'arch_server_ok': "Серверное окружение установлено",
        'arch_server_complete': "Для завершения настройки:",

        'arch_dev_title': "Установка окружения разработчика",
        'arch_dev_install': "Установка пакетов разработчика...",
        'arch_dev_aur': "Установка AUR-помощника (yay)...",
        'arch_dev_ok': "Окружение разработчика установлено",
        'arch_dev_extra': "Дополнительные шаги:",
        'arch_dev_aur_pkgs': "  # Установка дополнительных AUR-пакетов через yay",

        'arch_gaming_title': "Установка игрового окружения",
        'arch_gaming_install': "Установка игровых пакетов...",
        'arch_gaming_ok': "Игровое окружение установлено",
        'arch_gaming_list': "  Установленные программы:",

        # GPU
        'gpu_detecting': "Определение видеокарты...",
        'gpu_unknown': "Не удалось определить видеокарту. Пропускаем драйверы.",
        'gpu_detected': "  Обнаружена: {}",
        'gpu_vendor': "  Производитель: {}",
        'gpu_driver': "  Рекомендованный драйвер: {}",
        'gpu_no_packages': "Нет пакетов драйверов для {}. Пропускаем.",
        'gpu_installing': "Установка драйверов: {}",
        'gpu_failed': "Ошибка установки драйверов для {}",
        'gpu_ok': "Драйверы для {} установлены",
        'gpu_nvidia_config': "Конфигурация NVIDIA создана",
        'gpu_nvidia_mkinit': "NVIDIA добавлена в mkinitcpio",

        # Errors
        'error_pm': "Не удалось определить менеджер пакетов!",
        'error_not_arch': "Это не Arch Linux!",
        'error_root': "Запустите с sudo: sudo dpa {}",
        'error_mount': "/mnt не существует!",
        'error_mount_help': "Сначала смонтируйте корневую систему: mount /dev/sdX1 /mnt",
        'error_chroot': "Запустите после: arch-chroot /mnt",
        'error_pacstrap_removed': "Предупреждение: 'dpa pacstrap' удалён",
        'error_pacstrap_orig': "Используйте оригинальную команду pacstrap:",
        'error_pacstrap_cmd': "  sudo pacstrap /mnt base linux",
        'error_pacstrap_use': "Или используйте полезные команды DPA для Arch:",

        # Status
        'status_ok': "[OK]",
        'status_fail': "[FAIL]",
        'status_warn': "[WARN]",
        'status_info': "[INFO]",

        # Alias
        'alias_added': "Алиас добавлен: {} -> {}",
        'alias_builtin': "Встроенные алиасы:",
        'alias_custom': "Пользовательские алиасы: (нет)",
        'alias_add_help': "Добавьте алиас: dpa alias add --alias <имя> --real <пакет>",

        # Uninstall
        'uninstalling': "Удаление DPA...",
        'uninstalled': "DPA успешно удалён",
        'uninstall_removed': "  Удалён: {}",
        'uninstall_dir': "  Удалена директория: {}",
        'uninstall_warn': "  Предупреждение: Не удалось удалить {}: {}",

        # Interrupt
        'interrupt': "\nПрервано пользователем",
    }
}

def _(key: str, *args) -> str:
    """Получить строку на текущем языке"""
    string = STRINGS.get(LANG, STRINGS['en']).get(key, key)
    if args:
        return string.format(*args)
    return string

class DPACore:
    DB_PATH = Path.home() / ".local" / "share" / "dpa" / "packages.db"

    def __init__(self):
        self.db_path = self.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT,
                    description TEXT,
                    size INTEGER,
                    maintainer TEXT,
                    license TEXT,
                    url TEXT,
                    dependencies TEXT,
                    install_date TEXT,
                    source TEXT,
                    UNIQUE(name, source)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alias TEXT NOT NULL,
                    real_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    UNIQUE(alias, source)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    command TEXT NOT NULL,
                    packages TEXT,
                    status TEXT
                )
            """)

    def add_alias(self, alias: str, real_name: str, source: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO aliases (alias, real_name, source)
                VALUES (?, ?, ?)
            """, (alias, real_name, source))

    def resolve_package(self, name: str, source: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT real_name FROM aliases
                WHERE alias = ? AND source = ?
            """, (name, source))
            result = cur.fetchone()
            return result[0] if result else name

    def log_transaction(self, command: str, packages: List[str], status: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO history (timestamp, command, packages, status)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), command, json.dumps(packages), status))

    def get_history(self, limit: int = 20) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("""
                SELECT * FROM history
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

class DPAManager:
    PACKAGE_ALIASES = {
        'build-essential': {'apt': 'build-essential', 'dnf': 'gcc-c++', 'pacman': 'base-devel'},
        'python-pip': {'apt': 'python3-pip', 'dnf': 'python3-pip', 'pacman': 'python-pip'},
        'mysql': {'apt': 'mysql-server', 'dnf': 'mariadb-server', 'pacman': 'mariadb'},
        'postgresql': {'apt': 'postgresql', 'dnf': 'postgresql-server', 'pacman': 'postgresql'},
        'apache': {'apt': 'apache2', 'dnf': 'httpd', 'pacman': 'apache'},
        'docker': {'apt': 'docker.io', 'dnf': 'docker', 'pacman': 'docker'},
        'golang': {'apt': 'golang', 'dnf': 'golang', 'pacman': 'go'},
        'rust': {'apt': 'rustc', 'dnf': 'rust', 'pacman': 'rust'},
        'ffmpeg': {'apt': 'ffmpeg', 'dnf': 'ffmpeg', 'pacman': 'ffmpeg'},
        'imagemagick': {'apt': 'imagemagick', 'dnf': 'ImageMagick', 'pacman': 'imagemagick'},
        'htop': {'apt': 'htop', 'dnf': 'htop', 'pacman': 'htop'},
        'neofetch': {'apt': 'neofetch', 'dnf': 'neofetch', 'pacman': 'neofetch'},
        'vim': {'apt': 'vim', 'dnf': 'vim', 'pacman': 'vim'},
        'git': {'apt': 'git', 'dnf': 'git', 'pacman': 'git'},
        'curl': {'apt': 'curl', 'dnf': 'curl', 'pacman': 'curl'},
        'wget': {'apt': 'wget', 'dnf': 'wget', 'pacman': 'wget'},
        'nodejs': {'apt': 'nodejs', 'dnf': 'nodejs', 'pacman': 'nodejs'},
        'nginx': {'apt': 'nginx', 'dnf': 'nginx', 'pacman': 'nginx'},
        'redis': {'apt': 'redis-server', 'dnf': 'redis', 'pacman': 'redis'},
        'mongodb': {'apt': 'mongodb', 'dnf': 'mongodb-org', 'pacman': 'mongodb'},
        'elasticsearch': {'apt': 'elasticsearch', 'dnf': 'elasticsearch', 'pacman': 'elasticsearch'},
        'kibana': {'apt': 'kibana', 'dnf': 'kibana', 'pacman': 'kibana'},
        'grafana': {'apt': 'grafana', 'dnf': 'grafana', 'pacman': 'grafana'},
        'prometheus': {'apt': 'prometheus', 'dnf': 'prometheus', 'pacman': 'prometheus'},
        'jenkins': {'apt': 'jenkins', 'dnf': 'jenkins', 'pacman': 'jenkins'},
        'ansible': {'apt': 'ansible', 'dnf': 'ansible', 'pacman': 'ansible'},
        'terraform': {'apt': 'terraform', 'dnf': 'terraform', 'pacman': 'terraform'},
        'kubectl': {'apt': 'kubectl', 'dnf': 'kubectl', 'pacman': 'kubectl'},
        'helm': {'apt': 'helm', 'dnf': 'helm', 'pacman': 'helm'},
        'gnome': {'apt': 'gnome-shell', 'dnf': 'gnome-shell', 'pacman': 'gnome'},
        'kde': {'apt': 'plasma-desktop', 'dnf': 'plasma-desktop', 'pacman': 'plasma'},
        'xfce': {'apt': 'xfce4', 'dnf': 'xfce4', 'pacman': 'xfce4'},
        'cinnamon': {'apt': 'cinnamon', 'dnf': 'cinnamon', 'pacman': 'cinnamon'},
    }

    def __init__(self):
        self.core = DPACore()
        self.distro_info = self._get_distro_info()
        self.package_manager = self.distro_info['pm']
        self.pm_commands = self._get_pm_commands()
        self.lang = LANG

    def _get_distro_info(self) -> Dict:
        cache_file = Path.home() / ".cache" / "dpa" / "distro.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    if time.time() - cached.get('timestamp', 0) < 604800:
                        return cached
            except:
                pass

        info = self._detect_distro()
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(info, f)
        return info

    def _detect_distro(self) -> Dict:
        pm = None
        if os.path.exists('/usr/bin/dnf'): pm = 'dnf'
        elif os.path.exists('/usr/bin/apt'): pm = 'apt'
        elif os.path.exists('/usr/bin/pacman'): pm = 'pacman'
        elif os.path.exists('/usr/bin/zypper'): pm = 'zypper'
        elif os.path.exists('/usr/bin/yum'): pm = 'yum'

        distro = "Unknown"
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('NAME='):
                        distro = line.split('=', 1)[1].strip('"')
                        break
        except:
            pass

        if not pm:
            if os.path.exists('/etc/arch-release'): pm = 'pacman'
            elif os.path.exists('/etc/debian_version'): pm = 'apt'
            elif os.path.exists('/etc/fedora-release'): pm = 'dnf'

        if not pm:
            print(_('error_pm'), file=sys.stderr)
            sys.exit(1)

        return {'pm': pm, 'distro': distro, 'timestamp': int(time.time())}

    def _get_pm_commands(self) -> Dict:
        return {
            'dnf': {
                'install': ['sudo', 'dnf', 'install', '-y'],
                'remove': ['sudo', 'dnf', 'remove', '-y'],
                'update': ['sudo', 'dnf', 'update', '-y'],
                'upgrade': ['sudo', 'dnf', 'upgrade', '-y'],
                'search': ['dnf', 'search'],
                'info': ['dnf', 'info'],
                'list': ['dnf', 'list', 'installed'],
                'clean': ['sudo', 'dnf', 'clean', 'all'],
                'autoremove': ['sudo', 'dnf', 'autoremove', '-y']
            },
            'apt': {
                'install': ['sudo', 'apt', 'install', '-y'],
                'remove': ['sudo', 'apt', 'remove', '-y'],
                'update': ['sudo', 'apt', 'update'],
                'upgrade': ['sudo', 'apt', 'upgrade', '-y'],
                'search': ['apt', 'search'],
                'info': ['apt', 'show'],
                'list': ['apt', 'list', '--installed'],
                'clean': ['sudo', 'apt', 'clean'],
                'autoremove': ['sudo', 'apt', 'autoremove', '-y']
            },
            'pacman': {
                'install': ['sudo', 'pacman', '-S', '--noconfirm'],
                'remove': ['sudo', 'pacman', '-R', '--noconfirm'],
                'update': ['sudo', 'pacman', '-Syu', '--noconfirm'],
                'upgrade': ['sudo', 'pacman', '-Syu', '--noconfirm'],
                'search': ['pacman', '-Ss'],
                'info': ['pacman', '-Si'],
                'list': ['pacman', '-Q'],
                'clean': ['sudo', 'pacman', '-Scc', '--noconfirm'],
                'autoremove': ['sudo', 'pacman', '-Rns', '--noconfirm']
            },
            'zypper': {
                'install': ['sudo', 'zypper', 'install', '-y'],
                'remove': ['sudo', 'zypper', 'remove', '-y'],
                'update': ['sudo', 'zypper', 'refresh'],
                'upgrade': ['sudo', 'zypper', 'update', '-y'],
                'search': ['zypper', 'search'],
                'info': ['zypper', 'info'],
                'list': ['zypper', 'search', '--installed-only'],
                'clean': ['sudo', 'zypper', 'clean'],
                'autoremove': ['sudo', 'zypper', 'remove', '-u']
            },
            'yum': {
                'install': ['sudo', 'yum', 'install', '-y'],
                'remove': ['sudo', 'yum', 'remove', '-y'],
                'update': ['sudo', 'yum', 'update', '-y'],
                'upgrade': ['sudo', 'yum', 'upgrade', '-y'],
                'search': ['yum', 'search'],
                'info': ['yum', 'info'],
                'list': ['yum', 'list', 'installed'],
                'clean': ['sudo', 'yum', 'clean', 'all'],
                'autoremove': ['sudo', 'yum', 'autoremove', '-y']
            }
        }

    def _resolve_package(self, package: str) -> str:
        pm = self.package_manager
        if package in self.PACKAGE_ALIASES:
            aliases = self.PACKAGE_ALIASES[package]
            if pm in aliases:
                resolved = aliases[pm]
                if resolved != package:
                    print(f"Alias: {package} -> {resolved} ({pm.upper()})")
                return resolved

        resolved = self.core.resolve_package(package, pm)
        if resolved != package:
            print(f"Custom alias: {package} -> {resolved}")
            return resolved

        return package

    def _print_status(self, status: str, message: str):
        status_map = {
            'ok': _('status_ok'),
            'fail': _('status_fail'),
            'warn': _('status_warn'),
            'info': _('status_info')
        }
        prefix = status_map.get(status, _('status_info'))
        print(f"{prefix} {message}")

    def _print_command(self, cmd: List[str]):
        print(f"Executing: {' '.join(cmd)}")
        print("-" * 50)

    def _print_section(self, title: str):
        print(title)
        print("=" * len(title))

    def _run_command(self, cmd: List[str]) -> bool:
        if os.geteuid() != 0 and cmd[0] not in ['sudo', 'pacstrap']:
            if any(x in cmd for x in ['install', 'remove', 'update', 'upgrade', 'clean', 'autoremove']):
                cmd = ['sudo'] + cmd

        self._print_command(cmd)
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self._print_status('fail', f"Command failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            self._print_status('fail', f"Command not found: {cmd[0]}")
            return False

    # ============ MAIN COMMANDS ============

    def install(self, packages: List[str]) -> bool:
        self._print_status('info', _('installing', ' '.join(packages)))
        resolved = [self._resolve_package(pkg) for pkg in packages]
        cmd = self.pm_commands[self.package_manager]['install'] + resolved
        success = self._run_command(cmd)
        self.core.log_transaction("install", packages, "success" if success else "failed")
        if success:
            self._print_status('ok', _('completed', len(packages)))
        else:
            self._print_status('fail', _('failed'))
        return success

    def remove(self, packages: List[str]) -> bool:
        self._print_status('info', _('removing', ' '.join(packages)))
        cmd = self.pm_commands[self.package_manager]['remove'] + packages
        success = self._run_command(cmd)
        self.core.log_transaction("remove", packages, "success" if success else "failed")
        if success:
            self._print_status('ok', _('removed', len(packages)))
        else:
            self._print_status('fail', _('failed'))
        return success

    def update(self) -> bool:
        self._print_status('info', _('updating'))
        success = self._run_command(self.pm_commands[self.package_manager]['update'])
        if success:
            self._print_status('ok', _('updated'))
        else:
            self._print_status('fail', _('failed'))
        return success

    def upgrade(self) -> bool:
        self._print_status('info', _('upgrading'))
        success = self._run_command(self.pm_commands[self.package_manager]['upgrade'])
        if success:
            self._print_status('ok', _('upgraded'))
        else:
            self._print_status('fail', _('failed'))
        return success

    def search(self, query: str) -> bool:
        self._print_status('info', _('searching', query))
        return self._run_command(self.pm_commands[self.package_manager]['search'] + [query])

    def info(self, package: str) -> bool:
        self._print_status('info', _('info_pkg', package))
        return self._run_command(self.pm_commands[self.package_manager]['info'] + [package])

    def list_installed(self) -> bool:
        self._print_status('info', _('listing'))
        return self._run_command(self.pm_commands[self.package_manager]['list'])

    def clean(self) -> bool:
        self._print_status('info', _('cleaning'))
        success = self._run_command(self.pm_commands[self.package_manager]['clean'])
        if success:
            self._print_status('ok', _('cleaned'))
        else:
            self._print_status('fail', _('failed'))
        return success

    def autoremove(self) -> bool:
        self._print_status('info', _('autoremoving'))
        success = self._run_command(self.pm_commands[self.package_manager]['autoremove'])
        if success:
            self._print_status('ok', _('autoremoved'))
        else:
            self._print_status('fail', _('failed'))
        return success

    def history(self, limit: int = 20):
        self._print_section(_('history_title', limit))
        history = self.core.get_history(limit)
        if not history:
            self._print_status('info', _('history_empty'))
            return
        for entry in history:
            status_emoji = "[OK]" if entry['status'] == 'success' else "[FAIL]"
            packages = json.loads(entry['packages'])
            pkg_str = ' '.join(packages) if packages else '(none)'
            print(f"{status_emoji}   {entry['timestamp']}  {entry['command']:<10}  {pkg_str}")

    def show_distro(self):
        print(_('distro_title'))
        print(_('distro_name', self.distro_info['distro']))
        print(_('distro_pm', self.package_manager.upper()))
        print(_('distro_cache', Path.home() / '.cache' / 'dpa'))
        print(_('distro_config', Path.home() / '.config' / 'dpa'))
        print(_('distro_data', Path.home() / '.local' / 'share' / 'dpa'))

    def uninstall(self):
        import shutil
        self._print_status('info', _('uninstalling'))
        paths = [
            "/usr/local/bin/dpa",
            Path.home() / ".cache" / "dpa",
            Path.home() / ".config" / "dpa",
            Path.home() / ".local" / "share" / "dpa",
            Path.home() / ".local" / "state" / "dpa",
            Path.home() / ".bash_completion_dpa",
            Path.home() / ".zsh_completion_dpa",
            Path.home() / ".config" / "fish" / "completions" / "dpa.fish",
        ]
        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    print(_('uninstall_removed', path))
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    print(_('uninstall_dir', path))
            except Exception as e:
                print(_('uninstall_warn', path, e))
        for rc_file in [Path.home() / ".bashrc", Path.home() / ".zshrc"]:
            if rc_file.exists():
                try:
                    with open(rc_file, 'r') as f:
                        lines = f.readlines()
                    with open(rc_file, 'w') as f:
                        for line in lines:
                            if 'bash_completion_dpa' not in line and 'zsh_completion_dpa' not in line:
                                f.write(line)
                except:
                    pass
        self._print_status('ok', _('uninstalled'))

    # ============ GPU DETECTION ============

    def _detect_gpu(self) -> Dict:
        gpu_info = {
            'vendor': None,
            'model': None,
            'driver_packages': [],
            'recommended': None
        }

        try:
            result = subprocess.run(['lspci', '-nn'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'VGA' in line or '3D' in line:
                    if 'NVIDIA' in line or 'nvidia' in line.lower():
                        gpu_info['vendor'] = 'nvidia'
                        gpu_info['model'] = line.strip()
                        if 'GeForce RTX' in line:
                            gpu_info['recommended'] = 'nvidia-open'
                            gpu_info['driver_packages'] = ['nvidia-open', 'nvidia-utils', 'lib32-nvidia-utils']
                        elif any(x in line for x in ['GeForce GTX 16', 'GeForce GTX 10']):
                            gpu_info['recommended'] = 'nvidia'
                            gpu_info['driver_packages'] = ['nvidia', 'nvidia-utils', 'lib32-nvidia-utils']
                        else:
                            gpu_info['recommended'] = 'nvidia'
                            gpu_info['driver_packages'] = ['nvidia', 'nvidia-utils', 'lib32-nvidia-utils']
                        break

                    elif 'AMD' in line or 'amd' in line.lower() or 'Radeon' in line:
                        gpu_info['vendor'] = 'amd'
                        gpu_info['model'] = line.strip()
                        if any(x in line for x in ['RX 7', 'RX 6', 'RX 5']):
                            gpu_info['recommended'] = 'amdgpu'
                            gpu_info['driver_packages'] = ['mesa', 'lib32-mesa', 'xf86-video-amdgpu']
                        else:
                            gpu_info['recommended'] = 'radeon'
                            gpu_info['driver_packages'] = ['mesa', 'lib32-mesa', 'xf86-video-radeon']
                        break

                    elif 'Intel' in line or 'intel' in line.lower():
                        gpu_info['vendor'] = 'intel'
                        gpu_info['model'] = line.strip()
                        gpu_info['recommended'] = 'intel'
                        gpu_info['driver_packages'] = ['mesa', 'lib32-mesa', 'xf86-video-intel']
                        break

                    elif 'VMware' in line:
                        gpu_info['vendor'] = 'vmware'
                        gpu_info['model'] = 'VMware Virtual'
                        gpu_info['recommended'] = 'vmware'
                        gpu_info['driver_packages'] = ['xf86-video-vmware']
                        break

                    elif 'VirtualBox' in line:
                        gpu_info['vendor'] = 'virtualbox'
                        gpu_info['model'] = 'VirtualBox Virtual'
                        gpu_info['recommended'] = 'virtualbox'
                        gpu_info['driver_packages'] = ['xf86-video-vmware']
                        break
        except:
            pass

        if not gpu_info['vendor']:
            try:
                if os.path.exists('/proc/driver/nvidia'):
                    gpu_info['vendor'] = 'nvidia'
                    gpu_info['driver_packages'] = ['nvidia', 'nvidia-utils', 'lib32-nvidia-utils']
            except:
                pass

        return gpu_info

    def _install_gpu_drivers(self, target: str = "/mnt") -> bool:
        print(_('gpu_detecting'))
        gpu = self._detect_gpu()

        if not gpu['vendor']:
            self._print_status('warn', _('gpu_unknown'))
            return True

        print(_('gpu_detected', gpu['model']))
        print(_('gpu_vendor', gpu['vendor'].upper()))
        print(_('gpu_driver', gpu['recommended']))
        print()

        if not gpu['driver_packages']:
            self._print_status('warn', _('gpu_no_packages', gpu['vendor']))
            return True

        if gpu['vendor'] in ['nvidia']:
            gpu['driver_packages'].append('linux-headers')

        self._print_status('info', _('gpu_installing', ' '.join(gpu['driver_packages'])))
        cmd = ['pacstrap', target] + gpu['driver_packages']
        if not self._run_command(cmd):
            self._print_status('fail', _('gpu_failed', gpu['vendor']))
            return False

        if gpu['vendor'] == 'nvidia':
            self._configure_nvidia(target)

        self._print_status('ok', _('gpu_ok', gpu['vendor'].upper()))
        return True

    def _configure_nvidia(self, target: str):
        nvidia_config = f"""{target}/etc/X11/xorg.conf.d/00-nvidia.conf
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    Option         "NoLogo" "true"
    Option         "AllowEmptyInitialConfiguration"
    Option         "CoolBits" "28"
    Option         "RegistryDwords" "EnableBrightnessControl=1"
EndSection
"""
        config_dir = Path(f"{target}/etc/X11/xorg.conf.d")
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(f"{target}/etc/X11/xorg.conf.d/00-nvidia.conf", 'w') as f:
            f.write(nvidia_config)

        self._print_status('ok', _('gpu_nvidia_config'))

        if os.path.exists(f"{target}/etc/mkinitcpio.conf"):
            with open(f"{target}/etc/mkinitcpio.conf", 'r') as f:
                content = f.read()

            if 'nvidia' not in content:
                with open(f"{target}/etc/mkinitcpio.conf", 'a') as f:
                    f.write("\nMODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)\n")
                self._print_status('ok', _('gpu_nvidia_mkinit'))
                subprocess.run(f'arch-chroot {target} mkinitcpio -p linux', shell=True, check=False)

    # ============ ARCH LINUX COMMANDS ============

    def arch_install(self, target: str = "/mnt", packages: List[str] = None) -> bool:
        if packages is None:
            packages = ['base', 'linux', 'linux-firmware', 'vim', 'sudo', 'networkmanager']

        self._print_section(_('arch_install_title'))

        if self.package_manager != 'pacman':
            self._print_status('fail', _('error_not_arch'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('error_root', 'arch-install'))
            return False

        if not os.path.exists('/mnt'):
            self._print_status('fail', _('error_mount'))
            self._print_status('info', _('error_mount_help'))
            return False

        self._print_status('info', _('arch_install_base'))
        cmd = ['pacstrap', target] + packages
        if not self._run_command(cmd):
            return False

        self._print_status('info', _('arch_install_fstab'))
        subprocess.run(f'genfstab -U {target} >> {target}/etc/fstab', shell=True)

        self._print_status('info', _('arch_install_config'))
        self._setup_arch_chroot(target)

        self._print_status('ok', _('arch_install_ok'))
        print(_('arch_install_path', target))
        print()
        self._print_status('info', _('arch_install_next'))
        print(_('arch_install_step1', target))
        print(_('arch_install_step2'))
        print(_('arch_install_step3'))

        return True

    def _setup_arch_chroot(self, target: str):
        chroot_script = f"""{target}/root/setup-dpa.sh
#!/bin/bash
# Basic system configuration

# Locale
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# Timezone
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
hwclock --systohc

# Hostname
echo "archlinux" > /etc/hostname

# Hosts
cat > /etc/hosts << HOSTS
127.0.0.1   localhost
::1         localhost
127.0.1.1   archlinux.localdomain archlinux
HOSTS

# Network
systemctl enable NetworkManager

# Root password (temporary)
echo "root:root" | chpasswd

echo "Basic configuration completed"
"""

        with open(chroot_script, 'w') as f:
            f.write(chroot_script)

        os.chmod(chroot_script, 0o755)
        subprocess.run(f'arch-chroot {target} /root/setup-dpa.sh', shell=True)
        self._print_status('ok', "Basic configuration completed")

    def arch_config(self):
        self._print_section(_('arch_config_title'))

        if not os.path.exists('/etc/arch-release'):
            self._print_status('fail', _('arch_config_not_arch'))
            self._print_status('info', _('arch_config_chroot'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('arch_config_root'))
            return False

        print()
        self._print_status('info', _('arch_config_locale'))
        subprocess.run(['locale-gen'], check=False)

        print()
        self._print_status('info', _('arch_config_hostname'))
        hostname = input(_('arch_config_enter_host')) or "archlinux"
        with open('/etc/hostname', 'w') as f:
            f.write(hostname)

        print()
        self._print_status('info', _('arch_config_root_pw'))
        subprocess.run(['passwd'], check=False)

        print()
        self._print_status('info', _('arch_config_user'))
        create_user = input(_('arch_config_create')).lower()
        if create_user == 'y':
            username = input(_('arch_config_username'))
            if username:
                subprocess.run(['useradd', '-m', username], check=False)
                print(_('arch_config_set_pw', username))
                subprocess.run(['passwd', username], check=False)
                subprocess.run(['usermod', '-aG', 'wheel,audio,video,storage', username], check=False)
                with open('/etc/sudoers', 'a') as f:
                    f.write(f'\n{username} ALL=(ALL) ALL\n')
                self._print_status('ok', _('arch_config_user_ok', username))

        print()
        self._print_status('info', _('arch_config_boot'))
        boot_mode = input(_('arch_config_boot_mode')).lower()

        if boot_mode == 'uefi':
            subprocess.run(['grub-install', '--target=x86_64-efi', '--efi-directory=/boot', '--bootloader-id=GRUB'], check=False)
        elif boot_mode == 'bios':
            disk = input(_('arch_config_disk'))
            if disk:
                subprocess.run(['grub-install', f'--target=i386-pc', disk], check=False)
        else:
            self._print_status('warn', _('arch_config_skip'))

        if os.path.exists('/boot/grub'):
            subprocess.run(['grub-mkconfig', '-o', '/boot/grub/grub.cfg'], check=False)

        self._print_status('ok', _('arch_config_ok'))
        self._print_status('info', _('arch_config_exit'))

        return True

    def arch_desktop(self, de: str = "gnome", target: str = "/mnt") -> bool:
        desktop_envs = {
            'gnome': {
                'packages': ['gnome', 'gdm', 'gnome-tweaks'],
                'service': 'gdm',
                'desc': 'GNOME Desktop Environment'
            },
            'kde': {
                'packages': ['plasma', 'sddm', 'konsole', 'dolphin'],
                'service': 'sddm',
                'desc': 'KDE Plasma Desktop'
            },
            'xfce': {
                'packages': ['xfce4', 'xfce4-goodies', 'lightdm', 'lightdm-gtk-greeter'],
                'service': 'lightdm',
                'desc': 'XFCE Desktop Environment'
            },
            'cinnamon': {
                'packages': ['cinnamon', 'lightdm', 'lightdm-gtk-greeter'],
                'service': 'lightdm',
                'desc': 'Cinnamon Desktop Environment'
            },
            'mate': {
                'packages': ['mate', 'mate-extra', 'lightdm', 'lightdm-gtk-greeter'],
                'service': 'lightdm',
                'desc': 'MATE Desktop Environment'
            },
            'lxqt': {
                'packages': ['lxqt', 'sddm'],
                'service': 'sddm',
                'desc': 'LXQt Desktop Environment'
            },
            'i3': {
                'packages': ['i3-wm', 'i3status', 'i3lock', 'dmenu', 'alacritty'],
                'service': None,
                'desc': 'i3 Window Manager'
            },
            'sway': {
                'packages': ['sway', 'waybar', 'wofi', 'foot', 'swaylock'],
                'service': None,
                'desc': 'Sway Wayland Compositor'
            }
        }

        if self.package_manager != 'pacman':
            self._print_status('fail', _('arch_desktop_not_arch'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('arch_desktop_root'))
            return False

        if de not in desktop_envs:
            self._print_status('fail', _('arch_desktop_not_found', de))
            print(_('arch_desktop_available'))
            for key, env in desktop_envs.items():
                print(f"  {key:10} - {env['desc']}")
            print(_('arch_desktop_example'))
            return False

        env = desktop_envs[de]
        self._print_section(_('arch_desktop_title', env['desc']))

        if not os.path.exists(target):
            self._print_status('fail', _('arch_desktop_not_mount', target))
            self._print_status('info', _('arch_desktop_first'))
            return False

        self._print_status('info', _('arch_desktop_packages', ' '.join(env['packages'])))
        cmd = ['pacstrap', target] + env['packages']
        if not self._run_command(cmd):
            return False

        print()
        self._print_status('info', _('arch_desktop_gpu'))
        self._install_gpu_drivers(target)

        if env['service']:
            service_script = f"""{target}/root/enable-service.sh
#!/bin/bash
systemctl enable {env['service']}
"""
            with open(service_script, 'w') as f:
                f.write(service_script)
            os.chmod(service_script, 0o755)
            subprocess.run(f'arch-chroot {target} /root/enable-service.sh', shell=True)
            self._print_status('ok', _('arch_desktop_service', env['service']))

        self._print_status('ok', _('arch_desktop_ok', env['desc']))
        self._print_status('info', _('arch_desktop_reboot'))
        self._print_status('info', _('arch_desktop_pw'))

        return True

    def arch_server(self, target: str = "/mnt") -> bool:
        self._print_section(_('arch_server_title'))

        if self.package_manager != 'pacman':
            self._print_status('fail', _('error_not_arch'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('error_root', 'arch-server'))
            return False

        if not os.path.exists(target):
            self._print_status('fail', _('arch_desktop_not_mount', target))
            self._print_status('info', _('arch_desktop_first'))
            return False

        services = {
            'web': ['nginx', 'apache'],
            'database': ['mysql', 'postgresql', 'redis'],
            'devops': ['docker', 'ansible', 'terraform', 'kubectl', 'helm'],
            'monitoring': ['prometheus', 'grafana', 'elasticsearch', 'kibana'],
            'ci_cd': ['jenkins', 'gitlab-runner'],
            'message': ['rabbitmq', 'kafka'],
        }

        print()
        self._print_status('info', _('arch_server_available'))
        for category, pkgs in services.items():
            print(f"  {category}: {', '.join(pkgs)}")

        print()
        print(_('arch_server_enter'))
        print(_('arch_server_default'))
        user_input = input("> ").strip()

        if user_input:
            selected = user_input.split()
        else:
            selected = ['web', 'database', 'devops']

        packages = []
        for svc in selected:
            if svc in services:
                packages.extend(services[svc])
            else:
                self._print_status('warn', _('arch_server_unknown', svc))

        if not packages:
            self._print_status('fail', _('arch_server_none'))
            return False

        self._print_status('info', _('arch_server_install', ' '.join(packages)))
        cmd = ['pacstrap', target] + packages
        if not self._run_command(cmd):
            return False

        enable_script = f"""{target}/root/enable-services.sh
#!/bin/bash
# Enable services
systemctl enable nginx 2>/dev/null
systemctl enable mysqld 2>/dev/null
systemctl enable postgresql 2>/dev/null
systemctl enable redis 2>/dev/null
systemctl enable docker 2>/dev/null
systemctl enable jenkins 2>/dev/null
echo "Services enabled"
"""
        with open(enable_script, 'w') as f:
            f.write(enable_script)
        os.chmod(enable_script, 0o755)
        subprocess.run(f'arch-chroot {target} /root/enable-services.sh', shell=True)

        self._print_status('ok', _('arch_server_ok'))
        self._print_status('info', _('arch_install_path', target))
        self._print_status('info', _('arch_server_complete'))
        print(f"  arch-chroot {target}")
        print("  dpa arch-config  # Configure system")

        return True

    def arch_dev(self, target: str = "/mnt") -> bool:
        self._print_section(_('arch_dev_title'))

        if self.package_manager != 'pacman':
            self._print_status('fail', _('error_not_arch'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('error_root', 'arch-dev'))
            return False

        if not os.path.exists(target):
            self._print_status('fail', _('arch_desktop_not_mount', target))
            self._print_status('info', _('arch_desktop_first'))
            return False

        dev_packages = [
            'python', 'python-pip', 'nodejs', 'npm', 'go', 'rust', 'gcc',
            'git', 'vim', 'neovim', 'emacs', 'docker', 'docker-compose',
            'kubectl', 'helm', 'terraform', 'ansible',
            'htop', 'tree', 'tmux', 'neofetch', 'fzf', 'ripgrep',
            'bat', 'exa', 'zsh', 'fish'
        ]

        self._print_status('info', _('arch_dev_install'))
        cmd = ['pacstrap', target] + dev_packages
        if not self._run_command(cmd):
            return False

        self._print_status('info', _('arch_dev_aur'))
        yay_script = f"""{target}/root/install-yay.sh
#!/bin/bash
# Install yay
pacman -S --noconfirm base-devel git
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si --noconfirm
cd ..
rm -rf yay
echo "yay installed"
"""
        with open(yay_script, 'w') as f:
            f.write(yay_script)
        os.chmod(yay_script, 0o755)
        subprocess.run(f'arch-chroot {target} /root/install-yay.sh', shell=True)

        self._print_status('ok', _('arch_dev_ok'))
        self._print_status('info', _('arch_dev_extra'))
        print("  arch-chroot /mnt")
        print("  dpa arch-config  # Configure system")
        print(_('arch_dev_aur_pkgs'))

        return True

    def arch_gaming(self, target: str = "/mnt") -> bool:
        self._print_section(_('arch_gaming_title'))

        if self.package_manager != 'pacman':
            self._print_status('fail', _('error_not_arch'))
            return False

        if os.geteuid() != 0:
            self._print_status('fail', _('error_root', 'arch-gaming'))
            return False

        if not os.path.exists(target):
            self._print_status('fail', _('arch_desktop_not_mount', target))
            self._print_status('info', _('arch_desktop_first'))
            return False

        gaming_packages = [
            'steam', 'lutris', 'wine', 'winetricks', 'gamemode',
            'mangohud', 'goverlay', 'vkbasalt', 'proton-ge-custom',
            'discord', 'obs-studio', 'ffmpeg'
        ]

        self._print_status('info', _('arch_gaming_install'))
        cmd = ['pacstrap', target] + gaming_packages
        if not self._run_command(cmd):
            return False

        config_script = f"""{target}/root/gaming-setup.sh
#!/bin/bash
# Gaming environment setup

# Add user to groups
if [ -n "$SUDO_USER" ]; then
    usermod -aG games,audio,video,storage $SUDO_USER 2>/dev/null
fi

# Wine configuration
export WINEPREFIX=/home/$SUDO_USER/.wine 2>/dev/null

# Gamemode configuration
mkdir -p /etc/security/limits.d
cat > /etc/security/limits.d/99-gamemode.conf << LMITS
*       soft    rtprio   0
*       hard    rtprio   0
*       soft    nice     -10
*       hard    nice     -10
LMITS

echo "Gaming environment configured"
"""
        with open(config_script, 'w') as f:
            f.write(config_script)
        os.chmod(config_script, 0o755)
        subprocess.run(f'arch-chroot {target} /root/gaming-setup.sh', shell=True)

        self._print_status('ok', _('arch_gaming_ok'))
        print(_('arch_gaming_list'))
        print("  - Steam (Valve games)")
        print("  - Lutris (game manager)")
        print("  - Wine (Windows games)")
        print("  - Gamemode (performance optimization)")
        print("  - MangoHud (FPS monitoring)")
        print("  - OBS Studio (recording/streaming)")
        print("  - Discord (communication)")

        return True

def main():
    # Определяем язык для help
    lang = LANG  # "ru" или "en"

    # Описания для argparse на разных языках
    if lang == "ru":
        desc = "DPA - Универсальный менеджер пакетов"
        epilog = "Приводим порядок в управлении пакетами Linux | apt | dnf | pacman"

        # Команды
        install_help = "Установить пакет(ы)"
        remove_help = "Удалить пакет(ы)"
        update_help = "Обновить список пакетов"
        upgrade_help = "Обновить систему"
        list_help = "Список установленных пакетов"
        search_help = "Поиск пакетов"
        search_query = "Поисковый запрос"
        info_help = "Информация о пакете"
        info_package = "Имя пакета"
        clean_help = "Очистить кеш пакетов"
        autoremove_help = "Удалить ненужные пакеты"
        distro_help = "Информация о системе"
        history_help = "История транзакций"
        uninstall_help = "Удалить DPA"

        # Alias
        alias_help = "Управление алиасами"
        alias_action = "Действие (add/list)"
        alias_name = "Имя алиаса"
        alias_real = "Реальное имя пакета"

        # Arch
        arch_install_help = "Установка Arch Linux (базовая система)"
        arch_target = "Целевая директория (по умолчанию: /mnt)"
        arch_packages = "Дополнительные пакеты"
        arch_config_help = "Настройка Arch Linux (после chroot)"
        arch_desktop_help = "Установка Arch Linux с графическим окружением"
        arch_de = "Графическое окружение (по умолчанию: gnome)"
        arch_server_help = "Установка Arch Linux с серверным окружением"
        arch_dev_help = "Установка Arch Linux с окружением разработчика"
        arch_gaming_help = "Установка Arch Linux с игровым окружением"

        # Сообщение для pacstrap
        pacstrap_warn = "Предупреждение: 'dpa pacstrap' удалён"
        pacstrap_orig = "Используйте оригинальную команду pacstrap:"
        pacstrap_cmd = "  sudo pacstrap /mnt base linux"
        pacstrap_use = "Или используйте полезные команды DPA для Arch:"
        pacstrap_arch_install = "  sudo dpa arch-install     - Базовая установка"
        pacstrap_arch_desktop = "  sudo dpa arch-desktop     - Установка с графикой"
        pacstrap_arch_server = "  sudo dpa arch-server      - Серверное окружение"
        pacstrap_arch_dev = "  sudo dpa arch-dev         - Окружение разработчика"
        pacstrap_arch_gaming = "  sudo dpa arch-gaming      - Игровое окружение"
        pacstrap_arch_config = "  sudo dpa arch-config      - Настройка системы"
    else:
        desc = "DPA - Universal Package Manager"
        epilog = "Bringing order to Linux package management | apt | dnf | pacman"

        install_help = "Install package(s)"
        remove_help = "Remove package(s)"
        update_help = "Update package list"
        upgrade_help = "Upgrade system"
        list_help = "List installed packages"
        search_help = "Search packages"
        search_query = "Search query"
        info_help = "Show package information"
        info_package = "Package name"
        clean_help = "Clean package cache"
        autoremove_help = "Remove unused packages"
        distro_help = "Show system information"
        history_help = "Show transaction history"
        uninstall_help = "Uninstall DPA"

        alias_help = "Manage package aliases"
        alias_action = "Action (add/list)"
        alias_name = "Alias name"
        alias_real = "Real package name"

        arch_install_help = "Install Arch Linux (base system)"
        arch_target = "Target directory (default: /mnt)"
        arch_packages = "Additional packages"
        arch_config_help = "Configure Arch Linux (after chroot)"
        arch_desktop_help = "Install Arch Linux with desktop environment"
        arch_de = "Desktop environment (default: gnome)"
        arch_server_help = "Install Arch Linux with server environment"
        arch_dev_help = "Install Arch Linux with development environment"
        arch_gaming_help = "Install Arch Linux with gaming environment"

        pacstrap_warn = "Warning: 'dpa pacstrap' has been removed"
        pacstrap_orig = "Use the original pacstrap command:"
        pacstrap_cmd = "  sudo pacstrap /mnt base linux"
        pacstrap_use = "Or use DPA's useful Arch commands:"
        pacstrap_arch_install = "  sudo dpa arch-install     - Base installation"
        pacstrap_arch_desktop = "  sudo dpa arch-desktop     - Desktop installation"
        pacstrap_arch_server = "  sudo dpa arch-server      - Server environment"
        pacstrap_arch_dev = "  sudo dpa arch-dev         - Development environment"
        pacstrap_arch_gaming = "  sudo dpa arch-gaming      - Gaming environment"
        pacstrap_arch_config = "  sudo dpa arch-config      - System configuration"

    parser = argparse.ArgumentParser(
        description=desc,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command')

    # Main commands
    install = subparsers.add_parser('install', help=install_help)
    install.add_argument('packages', nargs='+', help=install_help)

    remove = subparsers.add_parser('remove', help=remove_help)
    remove.add_argument('packages', nargs='+', help=remove_help)

    subparsers.add_parser('update', help=update_help)
    subparsers.add_parser('upgrade', help=upgrade_help)
    subparsers.add_parser('list', help=list_help)

    search = subparsers.add_parser('search', help=search_help)
    search.add_argument('query', help=search_query)

    info = subparsers.add_parser('info', help=info_help)
    info.add_argument('package', help=info_package)

    subparsers.add_parser('clean', help=clean_help)
    subparsers.add_parser('autoremove', help=autoremove_help)
    subparsers.add_parser('distro', help=distro_help)
    subparsers.add_parser('history', help=history_help)
    subparsers.add_parser('uninstall', help=uninstall_help)

    # Alias management
    alias = subparsers.add_parser('alias', help=alias_help)
    alias.add_argument('action', choices=['add', 'list'], help=alias_action)
    alias.add_argument('--alias', help=alias_name)
    alias.add_argument('--real', help=alias_real)

    # Arch Linux commands
    arch_install_parser = subparsers.add_parser('arch-install', help=arch_install_help)
    arch_install_parser.add_argument('--target', default='/mnt', help=arch_target)
    arch_install_parser.add_argument('--packages', nargs='+',
        default=['base', 'linux', 'linux-firmware', 'vim', 'sudo', 'networkmanager'],
        help=arch_packages)

    subparsers.add_parser('arch-config', help=arch_config_help)

    arch_desktop_parser = subparsers.add_parser('arch-desktop', help=arch_desktop_help)
    arch_desktop_parser.add_argument('--de', default='gnome',
        choices=['gnome', 'kde', 'xfce', 'cinnamon', 'mate', 'lxqt', 'i3', 'sway'],
        help=arch_de)
    arch_desktop_parser.add_argument('--target', default='/mnt', help=arch_target)

    arch_server_parser = subparsers.add_parser('arch-server', help=arch_server_help)
    arch_server_parser.add_argument('--target', default='/mnt', help=arch_target)

    arch_dev_parser = subparsers.add_parser('arch-dev', help=arch_dev_help)
    arch_dev_parser.add_argument('--target', default='/mnt', help=arch_target)

    arch_gaming_parser = subparsers.add_parser('arch-gaming', help=arch_gaming_help)
    arch_gaming_parser.add_argument('--target', default='/mnt', help=arch_target)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    dpa = DPAManager()

    if args.command == 'install':
        dpa.install(args.packages)
    elif args.command == 'remove':
        dpa.remove(args.packages)
    elif args.command == 'update':
        dpa.update()
    elif args.command == 'upgrade':
        dpa.upgrade()
    elif args.command == 'search':
        dpa.search(args.query)
    elif args.command == 'info':
        dpa.info(args.package)
    elif args.command == 'list':
        dpa.list_installed()
    elif args.command == 'clean':
        dpa.clean()
    elif args.command == 'autoremove':
        dpa.autoremove()
    elif args.command == 'distro':
        dpa.show_distro()
    elif args.command == 'history':
        dpa.history()
    elif args.command == 'uninstall':
        dpa.uninstall()
    elif args.command == 'alias':
        if args.action == 'add' and args.alias and args.real:
            dpa.core.add_alias(args.alias, args.real, dpa.package_manager)
            print(_('alias_added', args.alias, args.real))
        elif args.action == 'list':
            print(_('alias_builtin'))
            for pkg, aliases in dpa.PACKAGE_ALIASES.items():
                if dpa.package_manager in aliases:
                    print(f"  {pkg} -> {aliases[dpa.package_manager]}")
            print()
            print(_('alias_custom'))
            print(_('alias_add_help'))
    elif args.command == 'arch-install':
        dpa.arch_install(args.target, args.packages)
    elif args.command == 'arch-config':
        dpa.arch_config()
    elif args.command == 'arch-desktop':
        dpa.arch_desktop(args.de, args.target)
    elif args.command == 'arch-server':
        dpa.arch_server(args.target)
    elif args.command == 'arch-dev':
        dpa.arch_dev(args.target)
    elif args.command == 'arch-gaming':
        dpa.arch_gaming(args.target)
    elif args.command == 'pacstrap':
        print(pacstrap_warn)
        print()
        print(pacstrap_orig)
        print(pacstrap_cmd)
        print()
        print(pacstrap_use)
        print(pacstrap_arch_install)
        print(pacstrap_arch_desktop)
        print(pacstrap_arch_server)
        print(pacstrap_arch_dev)
        print(pacstrap_arch_gaming)
        print(pacstrap_arch_config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(_('interrupt'))
        sys.exit(0)
EOF

    chmod +x /tmp/dpa.py
    sudo cp /tmp/dpa.py "${INSTALL_DIR}/${DPA_BIN}"

    # Сохраняем язык в конфиг
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_FILE" << EOF
{
    "language": "$LANG_CODE",
    "version": "$DPA_VERSION"
}
EOF

    if [ -f "${INSTALL_DIR}/${DPA_BIN}" ]; then
        echo -e "${GREEN}${MSG_CREATING} OK${NC}"
        rm -f /tmp/dpa.py
    else
        echo -e "${RED}${MSG_ERROR}${NC}"
        exit 1
    fi
}

# ============ INSTALLER FUNCTIONS ============
check_system() {
    echo -e "${BLUE}${MSG_CHECKING}${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}${MSG_PYTHON}${NC}"
        echo -e "${YELLOW}${MSG_INSTALL_PYTHON}${NC}"
        echo "  sudo apt install python3"
        echo "  sudo dnf install python3"
        echo "  sudo pacman -S python3"
        exit 1
    fi
    echo -e "${GREEN}Python 3: $(python3 --version)${NC}"

    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}${MSG_SUDO}${NC}"
        exit 1
    fi
    echo -e "${GREEN}Sudo privileges: OK${NC}"
}

setup_completion() {
    echo -e "${BLUE}${MSG_COMPLETION}${NC}"

    # Bash
    cat > ~/.bash_completion_dpa << 'EOF'
_dpa_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="install remove update upgrade search info list clean autoremove distro history alias uninstall arch-install arch-config arch-desktop arch-server arch-dev arch-gaming"

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        install|remove)
            ;;
        arch-desktop)
            COMPREPLY=( $(compgen -W "gnome kde xfce cinnamon mate lxqt i3 sway" -- ${cur}) )
            ;;
        *)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
    esac
}
complete -F _dpa_completion dpa
EOF

    if ! grep -q "bash_completion_dpa" ~/.bashrc 2>/dev/null; then
        echo "source ~/.bash_completion_dpa" >> ~/.bashrc
        echo -e "${GREEN}${MSG_BASH}${NC}"
    fi

    # Fish
    FISH_COMPLETION_DIR="$HOME/.config/fish/completions"
    mkdir -p "$FISH_COMPLETION_DIR"

    cat > "$FISH_COMPLETION_DIR/dpa.fish" << 'EOF'
complete -c dpa -f -a "install" -d "Install package(s)"
complete -c dpa -f -a "remove" -d "Remove package(s)"
complete -c dpa -f -a "update" -d "Update package list"
complete -c dpa -f -a "upgrade" -d "Upgrade system"
complete -c dpa -f -a "search" -d "Search packages"
complete -c dpa -f -a "info" -d "Package information"
complete -c dpa -f -a "list" -d "List installed packages"
complete -c dpa -f -a "clean" -d "Clean cache"
complete -c dpa -f -a "autoremove" -d "Remove unused packages"
complete -c dpa -f -a "distro" -d "System information"
complete -c dpa -f -a "history" -d "Transaction history"
complete -c dpa -f -a "uninstall" -d "Uninstall DPA"
complete -c dpa -f -a "alias" -d "Manage aliases"
complete -c dpa -f -a "arch-install" -d "Install Arch Linux"
complete -c dpa -f -a "arch-config" -d "Configure Arch Linux"
complete -c dpa -f -a "arch-desktop" -d "Install Arch with desktop"
complete -c dpa -f -a "arch-server" -d "Install Arch with server"
complete -c dpa -f -a "arch-dev" -d "Install Arch with dev tools"
complete -c dpa -f -a "arch-gaming" -d "Install Arch with gaming"
complete -c dpa -n "__fish_seen_subcommand_from arch-desktop" -l de -d "Desktop environment" -xa "gnome kde xfce cinnamon mate lxqt i3 sway"
EOF

    if command -v fish &> /dev/null; then
        echo -e "${GREEN}${MSG_FISH}${NC}"
    fi

    # ZSH
    if [ -n "$ZSH_VERSION" ] || [ -f ~/.zshrc ]; then
        cat > ~/.zsh_completion_dpa << 'EOF'
_dpa() {
    local -a commands
    commands=(
        'install:Install package(s)'
        'remove:Remove package(s)'
        'update:Update package list'
        'upgrade:Upgrade system'
        'search:Search packages'
        'info:Package information'
        'list:List installed packages'
        'clean:Clean cache'
        'autoremove:Remove unused packages'
        'distro:System information'
        'history:Transaction history'
        'alias:Manage aliases'
        'uninstall:Uninstall DPA'
        'arch-install:Install Arch Linux'
        'arch-config:Configure Arch Linux'
        'arch-desktop:Install Arch with desktop'
        'arch-server:Install Arch with server'
        'arch-dev:Install Arch with dev tools'
        'arch-gaming:Install Arch with gaming'
    )
    _describe 'command' commands
    case $words[2] in
        arch-desktop)
            _values 'desktop environment' gnome kde xfce cinnamon mate lxqt i3 sway
            ;;
    esac
}
compdef _dpa dpa
EOF
        if ! grep -q "zsh_completion_dpa" ~/.zshrc 2>/dev/null; then
            echo "source ~/.zsh_completion_dpa" >> ~/.zshrc
            echo -e "${GREEN}${MSG_ZSH}${NC}"
        fi
    fi
}

create_directories() {
    echo -e "${BLUE}${MSG_DIRS}${NC}"
    mkdir -p "$CONFIG_DIR" "$HOME/.cache/dpa" "$HOME/.local/share/dpa"
    echo -e "${GREEN}${MSG_DIRS_OK}${NC}"
}

show_usage() {
    echo -e "\n${GREEN}${MSG_INSTALLED}${NC}"
    echo -e "${GREEN}${MSG_LANG}: ${LANG_NAME}${NC}"
    echo -e "\n${BLUE}${MSG_MAIN}${NC}"
    echo -e "  ${CYAN}dpa install vlc${NC}        - Install VLC"
    echo -e "  ${CYAN}dpa update${NC}            - Update package list"
    echo -e "  ${CYAN}dpa upgrade${NC}           - Upgrade system"
    echo -e "  ${CYAN}dpa search python${NC}     - Search packages"
    echo -e "  ${CYAN}dpa list${NC}              - List installed packages"
    echo -e "  ${CYAN}dpa history${NC}           - Transaction history"
    echo -e "  ${CYAN}dpa distro${NC}            - System information"
    echo -e "  ${CYAN}dpa uninstall${NC}         - Uninstall DPA"

    echo -e "\n${BLUE}${MSG_ARCH}${NC}"
    echo -e "  ${CYAN}sudo dpa arch-install${NC}   - Base installation"
    echo -e "  ${CYAN}sudo dpa arch-desktop --de kde${NC} - Install with KDE"
    echo -e "  ${CYAN}sudo dpa arch-server${NC}    - Server environment"
    echo -e "  ${CYAN}sudo dpa arch-dev${NC}       - Development environment"
    echo -e "  ${CYAN}sudo dpa arch-gaming${NC}    - Gaming environment"
    echo -e "  ${CYAN}sudo dpa arch-config${NC}    - System configuration"

    echo -e "\n${BLUE}${MSG_ALIAS}${NC}"
    echo -e "  ${CYAN}dpa alias add --alias build-essential --real gcc-c++${NC}"
    echo -e "  ${CYAN}dpa alias list${NC}         - List aliases"

    echo -e "\n${BLUE}${MSG_SHELL}${NC}"
    echo -e "  ${CYAN}bash${NC} - completion added"
    echo -e "  ${CYAN}zsh${NC}  - completion added"
    if command -v fish &> /dev/null; then
        echo -e "  ${CYAN}fish${NC} - completion added"
    else
        echo -e "  ${YELLOW}fish${NC} - install fish for completion"
    fi

    echo -e "\n${YELLOW}${MSG_RELOAD}${NC}"
}

# ============ MAIN INSTALLATION ============
main_install() {
    # Выбор языка
    select_language

    clear
    print_banner
    echo -e "${YELLOW}${MSG_INSTALLING}${NC}\n"

    check_system
    echo ""
    create_directories
    echo ""
    create_dpa_script
    echo ""
    setup_completion
    echo ""

    echo -e "${BLUE}${MSG_TESTING}${NC}"
    if dpa distro 2>/dev/null; then
        echo -e "${GREEN}${MSG_WORKS}${NC}"
    fi
    echo ""

    show_usage
}

main_install
