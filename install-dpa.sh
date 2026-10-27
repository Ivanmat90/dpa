#!/usr/bin/env bash
# install-dpa.sh - установщик DPA / DPA installer
#
# Запуск из клона репозитория:   ./install-dpa.sh [--lang ru|en]
# Или без клонирования:          curl -fsSL https://raw.githubusercontent.com/Ivanmat90/dpa/main/install-dpa.sh | bash
#
# Скрипт собирает пакет dpa/ в один исполняемый файл (zipapp) и кладёт его
# в /usr/local/bin/dpa. Ничего, кроме Python 3.8+, не требуется.

set -euo pipefail

DPA_REPO="${DPA_REPO:-Ivanmat90/dpa}"
DPA_REF="${DPA_REF:-main}"
INSTALL_PATH="${DPA_INSTALL_PATH:-/usr/local/bin/dpa}"
LANG_CODE=""

# ---------- аргументы ----------
while [ $# -gt 0 ]; do
    case "$1" in
        --lang) LANG_CODE="${2:-}"; shift 2 ;;
        --lang=*) LANG_CODE="${1#--lang=}"; shift ;;
        -h|--help) echo "Usage: install-dpa.sh [--lang en|ru]"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

# ---------- цвета ----------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'
    BLUE=$'\033[0;34m'; CYAN=$'\033[0;36m'; GRAY=$'\033[0;90m'; NC=$'\033[0m'
else
    RED=""; GREEN=""; YELLOW=""; BLUE=""; CYAN=""; GRAY=""; NC=""
fi

# ---------- выбор языка ----------
detect_lang() {
    case "${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}" in ru*) echo ru ;; *) echo en ;; esac
}

select_language() {
    if [ -n "$LANG_CODE" ]; then return; fi
    if [ -r /dev/tty ] && [ -w /dev/tty ]; then
        {
            echo ""
            echo "Select language / Выберите язык:"
            echo "  1) English"
            echo "  2) Русский"
        } > /dev/tty
        printf "Enter your choice / Введите номер (1-2) [%s]: " \
            "$([ "$(detect_lang)" = ru ] && echo 2 || echo 1)" > /dev/tty
        local choice=""
        read -r choice < /dev/tty || true
        case "$choice" in
            1|en|EN) LANG_CODE=en ;;
            2|ru|RU) LANG_CODE=ru ;;
            *) LANG_CODE="$(detect_lang)" ;;
        esac
    else
        LANG_CODE="$(detect_lang)"
    fi
}

# m KEY [args...] - сообщение на выбранном языке
m() {
    local key="$1"; shift
    local text
    case "$LANG_CODE:$key" in
        ru:checking)   text="Проверка системы..." ;;
        en:checking)   text="Checking system..." ;;
        ru:nopython)   text="Python 3.8+ не найден. Установите: apt install python3 | dnf install python3 | pacman -S python" ;;
        en:nopython)   text="Python 3.8+ not found. Install: apt install python3 | dnf install python3 | pacman -S python" ;;
        ru:nosudo)     text="Нужны права root или sudo" ;;
        en:nosudo)     text="root privileges or sudo required" ;;
        ru:source_local) text="Источник: локальная копия (%s)" ;;
        en:source_local) text="Source: local copy (%s)" ;;
        ru:source_net)   text="Источник: загрузка %s" ;;
        en:source_net)   text="Source: downloading %s" ;;
        ru:nocurl)     text="Нужен curl или wget для загрузки" ;;
        en:nocurl)     text="curl or wget is required to download" ;;
        ru:dlfail)     text="Не удалось скачать архив проекта" ;;
        en:dlfail)     text="Could not download the project archive" ;;
        ru:nosrc)      text="В архиве не найден пакет dpa/" ;;
        en:nosrc)      text="Package dpa/ not found in the archive" ;;
        ru:building)   text="Сборка исполняемого файла..." ;;
        en:building)   text="Building the executable..." ;;
        ru:installing) text="Установка в %s..." ;;
        en:installing) text="Installing to %s..." ;;
        ru:setup)      text="Настройка языка и автодополнения..." ;;
        en:setup)      text="Configuring language and shell completion..." ;;
        ru:done)       text="DPA успешно установлен!" ;;
        en:done)       text="DPA installed successfully!" ;;
        ru:fail)       text="Ошибка: установка не удалась" ;;
        en:fail)       text="Error: installation failed" ;;
        ru:hint)       text="Попробуйте:  dpa --help   |   dpa install --dry-run vlc" ;;
        en:hint)       text="Try:  dpa --help   |   dpa install --dry-run vlc" ;;
        ru:reload)     text="Перезапустите терминал (или: source ~/.bashrc), чтобы заработало автодополнение" ;;
        en:reload)     text="Restart your terminal (or: source ~/.bashrc) to enable completion" ;;
        *) text="$key" ;;
    esac
    # shellcheck disable=SC2059
    printf "$text" "$@"
}

say()  { printf "%s\n" "${BLUE}==>${NC} $*"; }
good() { printf "%s\n" "${GREEN}  OK${NC} $*"; }
die()  { printf "%s\n" "${RED}  ERROR${NC} $*" >&2; exit 1; }

banner() {
    printf "%s" "$CYAN"
    cat <<'ART'

  ██████████   ███████████    █████████
 ▒▒███▒▒▒▒███ ▒▒███▒▒▒▒▒███  ███▒▒▒▒▒███
  ▒███   ▒▒███ ▒███    ▒███ ▒███    ▒███
  ▒███    ▒███ ▒██████████  ▒███████████
  ▒███    ▒███ ▒███▒▒▒▒▒▒   ▒███▒▒▒▒▒███
  ▒███    ███  ▒███         ▒███    ▒███
  ██████████   █████        █████   █████
 ▒▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒        ▒▒▒▒▒   ▒▒▒▒▒
ART
    printf "%s" "$NC"
    printf "%s\n\n" "${GRAY}  apt | dnf | pacman  -  https://github.com/${DPA_REPO}${NC}"
}

# ---------- основной ход ----------
select_language
banner

say "$(m checking)"
command -v python3 >/dev/null 2>&1 || die "$(m nopython)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || die "$(m nopython)"
python3 -c 'import zipapp' 2>/dev/null || die "python3 zipapp module missing (install python3 stdlib)"
good "$(python3 --version)"

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    command -v sudo >/dev/null 2>&1 || die "$(m nosudo)"
    sudo -v || die "$(m nosudo)"
    SUDO="sudo"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
trap 'echo; die "$(m fail)"' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo .)"
if [ -f "$SCRIPT_DIR/dpa/cli.py" ]; then
    SRC="$SCRIPT_DIR"
    say "$(m source_local "$SRC")"
else
    URL="https://github.com/${DPA_REPO}/archive/refs/heads/${DPA_REF}.tar.gz"
    say "$(m source_net "$URL")"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$URL" -o "$TMP/src.tar.gz" || die "$(m dlfail)"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$TMP/src.tar.gz" "$URL" || die "$(m dlfail)"
    else
        die "$(m nocurl)"
    fi
    mkdir -p "$TMP/src"
    tar -xzf "$TMP/src.tar.gz" -C "$TMP/src" --strip-components=1
    SRC="$TMP/src"
fi
[ -f "$SRC/dpa/cli.py" ] || die "$(m nosrc)"

say "$(m building)"
mkdir -p "$TMP/build"
cp -r "$SRC/dpa" "$TMP/build/dpa"
find "$TMP/build" -name '__pycache__' -prune -exec rm -rf {} +
python3 -m zipapp "$TMP/build" -m "dpa.cli:entry" -p "/usr/bin/env python3" -o "$TMP/dpa"
chmod 755 "$TMP/dpa"
"$TMP/dpa" --version >/dev/null || die "$(m fail)"

say "$(m installing "$INSTALL_PATH")"
$SUDO mkdir -p "$(dirname "$INSTALL_PATH")"
$SUDO install -m 755 "$TMP/dpa" "$INSTALL_PATH"

say "$(m setup)"
"$INSTALL_PATH" lang "$LANG_CODE" || true
"$INSTALL_PATH" completion --install || true

echo ""
good "$(m done)"
"$INSTALL_PATH" distro || true
echo ""
printf "%s\n" "${YELLOW}$(m hint)${NC}"
printf "%s\n" "${GRAY}$(m reload)${NC}"
