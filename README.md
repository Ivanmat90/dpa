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
Без клонирования: `curl -fsSL https://raw.githubusercontent.com/Ivanmat90/dpa/Remake/install-dpa.sh | bash`

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
| `distro`, `lang [en\|ru]`, `completion` | система, язык, автодополнение |
| `arch-install`, `arch-config`, `arch-desktop`, `arch-server`, `arch-dev`, `arch-gaming` | установка и настройка Arch Linux |

Общие флаги (работают до и после команды): `-y/--yes`, `--dry-run`, `--no-color`.
Без `-y` вопросы задаёт сам пакетный менеджер, так что видно полный список изменений.
Язык: `dpa lang ru` или переменная `DPA_LANG`. Переменная `DPA_BACKEND=apt|dnf|pacman`
принудительно выбирает бэкенд (удобно для проверки с `--dry-run`).

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
├── tests/test_dpa.py       python3 -m unittest discover -s tests
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
    └── arch/               common, gpu, install, configure, desktop, server, dev, gaming
```

### Как расширять

* **Новый дистрибутив/менеджер** - один файл в `dpa/backends/` (класс с `cmd_*`-методами)
  и строка в `BACKENDS`.
* **Новая команда** - запись в `COMMANDS` (`cli.py`), обработчик в `dispatch`.
  Справка и автодополнение обновятся сами.
* **Новый язык** - `dpa/locales/<код>.py` и код в `SUPPORTED` (`i18n.py`);
  тест следит, чтобы ключи совпадали.
* **Новый алиас** - запись в `BUILTIN` (`aliases.py`); указываются только отличия.
