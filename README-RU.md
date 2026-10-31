# DPA - Dnf Pacman Apt

Единый интерфейс к `apt`, `dnf` и `pacman`: одни и те же команды на Debian/Ubuntu,
Fedora/RHEL и Arch. Без внешних зависимостей, нужен только Python 3.8+.

```
dpa install vlc          # поставить пакет
dpa upgrade              # обновить систему
dpa search python        # найти пакет
dpa install --dry-run docker   # показать, что будет выполнено, ничего не меняя
```

## Установка

```bash
git clone https://github.com/Ivanmat90/dpa.git
cd dpa
./install-dpa.sh            # спросит язык; или: ./install-dpa.sh --lang ru
```

Установщик собирает пакет `dpa/` в один исполняемый файл `/usr/local/bin/dpa`,
выбирает язык и ставит автодополнение (bash/zsh/fish).
Без клонирования: `curl -fsSL https://raw.githubusercontent.com/Ivanmat90/dpa/main/install-dpa.sh | bash`

Удаление: `dpa uninstall` (`--keep-data` оставит историю и алиасы).

## Команды

| Команда | Что делает |
|---|---|
| `install` (`i`, `add`) / `remove` (`rm`) | установить / удалить пакеты |
| `update` / `upgrade` (`up`) | обновить сведения о пакетах / обновить систему |
| `search` (`s`), `info` (`show`), `list` (`ls`) | поиск, информация, список (`dpa ls python` - с фильтром) |
| `clean`, `autoremove` | очистить кеш / убрать ненужные пакеты |
| `history` (`log`) | история (`-n 50` - сколько записей) |
| `alias add\|list\|remove` | свои имена пакетов (`dpa alias add web nginx`) |
| `tui` | интерактивный интерфейс с мышью (необязательный, см. ниже) |
| `distro`, `lang [en\|ru]`, `completion` | система, язык, автодополнение |
| `arch-install`, `arch-config`, `arch-desktop`, `arch-server`, `arch-dev`, `arch-gaming` | установка и настройка Arch Linux |

Общие флаги (работают до и после команды): `-y/--yes`, `--dry-run`, `--no-color`.
Без `-y` вопросы задаёт сам пакетный менеджер, так что видно полный список изменений.
Язык: `dpa lang ru` или переменная `DPA_LANG`. Переменная `DPA_BACKEND=apt|dnf|pacman`
принудительно выбирает бэкенд (удобно для проверки с `--dry-run`).

## TUI - интерактивный интерфейс (необязательно)

```bash
dpa tui                     # запуск; если нужной библиотеки нет - предложит поставить
dpa tui --install-deps      # только поставить зависимость (или ./install-dpa.sh --with-tui)
```

Обычный CLI работает без каких-либо сторонних библиотек. TUI построен на
[Textual](https://textual.textualize.io/) и ставится **отдельно**: dpa создаёт приватное
виртуальное окружение `~/.local/share/dpa/tui-venv` (root не нужен, системный Python не
затрагивается, нужен интернет). Если Textual уже есть в системе, используется он.

Вкладки: **Пакеты** (поиск, отметки, установка и удаление), **Установленные** (фильтр),
**Система** (update/upgrade/clean/autoremove), **История**, **Алиасы**, **Настройки** (язык).
Работает мышь: клики по вкладкам, кнопкам и строкам, прокрутка колесом.

| Клавиша | Действие |
|---|---|
| `/` | перейти к поиску |
| `Enter` в поиске | искать |
| `Space` / `i` / `r` в таблице | отметить / установить / удалить |
| `1`-`6` | вкладки |
| `F5` | обновить данные |
| `Ctrl+P` | палитра команд Textual (в том числе смена темы) |
| `q`, `Ctrl+Q` | выход |

Операции, меняющие систему, выполняются **в обычном терминале**: TUI на время уступает
экран, поэтому работают запрос пароля sudo и вопросы apt/dnf/pacman; потом вы возвращаетесь
в TUI. `dpa --dry-run tui` покажет, что будет выполнено, ничего не меняя.
Смена языка в настройках применяется после перезапуска TUI.

### Установка Arch Linux с live-ISO

```bash
# разметить диски, смонтировать корень в /mnt (и ESP в /mnt/boot или /mnt/boot/efi)
sudo dpa arch-install                 # pacstrap + fstab + NetworkManager
sudo dpa arch-config                  # локаль, пояс, hostname, пароли, пользователь, GRUB
sudo dpa arch-desktop --de kde        # окружение + драйверы видеокарты
sudo dpa arch-dev --user ivan         # инструменты разработчика (+yay для пользователя)
umount -R /mnt && reboot
```

Все `arch-*` команды работают с `--target` (по умолчанию `/mnt`) прямо с live-ISO,
`arch-chroot` вручную не нужен. Сначала попробуйте с `--dry-run`.

## Структура проекта

```
dpa/
├── install-dpa.sh          установщик (собирает zipapp, ставит автодополнение)
├── pyproject.toml          метаданные (pip install -e . для разработки)
├── tests/                  python3 -m unittest discover -s tests
│   ├── test_dpa.py         ядро, бэкенды, Arch, автодополнение
│   └── test_tui.py         TUI (тесты на настоящем Textual идут, если он установлен)
└── dpa/                    пакет
    ├── cli.py              разбор аргументов, таблица команд, диспетчер
    ├── manager.py          операции над пакетами (заголовки, история, время)
    ├── backends/           apt.py, dnf.py, pacman.py + автоопределение
    ├── aliases.py, db.py   имена пакетов между дистрибутивами, SQLite
    ├── ui.py               цвета, иконки, таблицы, баннер, вопросы
    ├── i18n.py, locales/   переводы: en.py, ru.py
    ├── runtime.py          запуск команд: sudo, --dry-run, ошибки
    ├── config.py           пути и конфиг (корректно работает под sudo)
    ├── completions.py      bash/zsh/fish строятся из argparse-парсера
    ├── selfmanage.py       установка автодополнения и uninstall
    ├── tui/                необязательный интерфейс
    │   ├── __init__.py     запуск, предложение установить Textual (Textual не нужен)
    │   ├── deps.py         приватный venv с Textual
    │   ├── model.py        данные для TUI (поиск, алиасы, история), без Textual
    │   └── app.py          сам интерфейс на Textual (импортируется только при запуске)
    └── arch/               common, gpu, install, configure, desktop, server, dev, gaming
```

### Как расширять

* **Новый дистрибутив/менеджер** - один файл в `dpa/backends/` (класс с `cmd_*`-методами)
  и строка в `BACKENDS`.
* **Новая команда** - запись в `COMMANDS` (`cli.py`), обработчик в `dispatch`.
  Справка и автодополнение обновятся сами.
* **Новая вкладка TUI** - класс панели и `TabPane` в `dpa/tui/app.py`, данные - метод в `tui/model.py`.
* **Новый язык** - `dpa/locales/<код>.py` и код в `SUPPORTED` (`i18n.py`);
  тест следит, чтобы ключи совпадали.
* **Новый алиас** - запись в `BUILTIN` (`aliases.py`); указываются только отличия.
