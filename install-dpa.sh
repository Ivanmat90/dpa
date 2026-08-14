#!/bin/bash
# install-dpa.sh - Самодостаточный инсталлятор DPA
# Версия: 2.0.0
# GitHub: https://github.com/Ivanmat90/dpa

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
DPA_VERSION="2.2.0"
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
    MSG_CREATING="Установка DPA..."
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
    MSG_CREATING="Installing DPA..."
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
    echo "  ██████████   ███████████    █████████"
    echo " ▒▒███▒▒▒▒███ ▒▒███▒▒▒▒▒███  ███▒▒▒▒▒███ "
    echo "  ▒███   ▒▒███ ▒███    ▒███ ▒███    ▒███ "
    echo "  ▒███    ▒███ ▒██████████  ▒███████████ "
    echo "  ▒███    ▒███ ▒███▒▒▒▒▒▒   ▒███▒▒▒▒▒███ "
    echo "  ▒███    ███  ▒███         ▒███    ▒███ "
    echo "  ██████████   █████        █████   █████"
    echo " ▒▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒        ▒▒▒▒▒   ▒▒▒▒▒ "
    echo -e "${NC}"
    echo -e "${GREEN}  ${MSG_BANNER} v${DPA_VERSION}${NC}"
    echo -e "${YELLOW}  apt | dnf | pacman | zypper | yum${NC}"
    echo -e "${PURPLE}  https://github.com/Ivanmat90/dpa${NC}"
    echo ""
}

# ============ ВЕСЬ КОД DPA ВСТРОЕН (С ПОДДЕРЖКОЙ ЯЗЫКОВ) ============
create_dpa_script() {
    echo -e "${BLUE}${MSG_CREATING}${NC}"

    # Скачиваем Python скрипт
    curl --output-dir /tmp -O https://raw.githubusercontent.com/Ivanmat90/dpa/main/dpa.py

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
