"""Строки интерфейса (ru)."""
from __future__ import annotations

STRINGS = {
    "installing": "Установка: {}",

    "removing": "Удаление: {}",

    "updating": "Обновление списка пакетов",

    "upgrading": "Обновление системы",

    "searching": "Поиск: {}",

    "info_pkg": "Информация о пакете: {}",

    "listing": "Список установленных пакетов",

    "cleaning": "Очистка кеша пакетов",

    "autoremoving": "Удаление ненужных пакетов",

    "completed": "Установка завершена: {} пакет(ов)",

    "removed": "Удаление завершено: {} пакет(ов)",

    "updated": "Список пакетов обновлён",

    "upgraded": "Система обновлена",

    "cleaned": "Кеш очищен",

    "autoremoved": "Ненужные пакеты удалены",

    "failed": "Операция не удалась",

    "history_title": "История транзакций (последние {})",
    "history_empty": "История пуста",

    "distro_title": "Информация о системе",

    "arch_install_title": "Установка Arch Linux",
    "arch_install_base": "Установка базовой системы...",
    "arch_install_fstab": "Генерация fstab...",
    "arch_install_config": "Настройка системы...",
    "arch_install_ok": "Arch Linux успешно установлен",
    "arch_install_path": "  Система установлена в: {}",
    "arch_install_next": "Следующие шаги:",
    "arch_install_step1": "  1. Настройте систему: sudo dpa arch-config --target {}",
    "arch_install_step2": "  2. По желанию: sudo dpa arch-desktop --de gnome",
    "arch_install_step3": "  3. Отмонтируйте (umount -R /mnt) и перезагрузитесь",
    "arch_config_title": "Настройка Arch Linux",
    "arch_config_locale": "Настройка локалей...",
    "arch_config_hostname": "Настройка имени хоста...",
    "arch_config_enter_host": "Имя хоста",
    "arch_config_root_pw": "Настройка пароля root...",
    "arch_config_user": "Создание пользователя...",
    "arch_config_create": "Создать пользователя?",
    "arch_config_username": "Имя пользователя",
    "arch_config_set_pw": "Установите пароль для {}",
    "arch_config_user_ok": "Пользователь {} создан",
    "arch_config_boot": "Установка загрузчика...",
    "arch_config_boot_mode": "Режим загрузки (uefi/bios)",
    "arch_config_disk": "Диск (например, /dev/sda)",
    "arch_config_skip": "Пропускаем установку загрузчика",
    "arch_config_ok": "Настройка завершена",
    "arch_config_exit": "Отмонтируйте (umount -R /mnt) и перезагрузитесь",
    "arch_desktop_title": "Установка {}",
    "arch_desktop_not_found": "Окружение '{}' не найдено!",
    "arch_desktop_available": "Доступные окружения:",
    "arch_desktop_example": "Пример: dpa arch-desktop --de gnome",
    "arch_desktop_packages": "Установка пакетов: {}",
    "arch_desktop_gpu": "Определение и установка драйверов для видеокарты...",
    "arch_desktop_ok": "{} установлен",
    "arch_desktop_reboot": "Перезагрузитесь и войдите в систему",
    "arch_server_title": "Установка серверного окружения Arch Linux",
    "arch_server_available": "Доступные сервисы:",
    "arch_server_enter": "Введите названия или номера категорий через пробел (Enter - стандартные):",
    "arch_server_default": "Стандартные: web, database, devops",
    "arch_server_unknown": "Неизвестный сервис: {}",
    "arch_server_none": "Нет пакетов для установки",
    "arch_server_install": "Установка: {}",
    "arch_server_ok": "Серверное окружение установлено",
    "arch_server_complete": "Для завершения настройки:",
    "arch_dev_title": "Установка окружения разработчика",
    "arch_dev_install": "Установка пакетов разработчика...",
    "arch_dev_aur": "Установка AUR-помощника (yay)...",
    "arch_dev_ok": "Окружение разработчика установлено",
    "arch_dev_extra": "Дополнительные шаги:",
    "arch_gaming_title": "Установка игрового окружения",
    "arch_gaming_install": "Установка игровых пакетов...",
    "arch_gaming_ok": "Игровое окружение установлено",
    "arch_gaming_list": "  Установленные программы:",

    "gpu_detecting": "Определение видеокарты...",
    "gpu_unknown": "Не удалось определить видеокарту. Пропускаем драйверы.",
    "gpu_detected": "  Обнаружена: {}",
    "gpu_vendor": "  Производитель: {}",
    "gpu_failed": "Ошибка установки драйверов для {}",
    "gpu_ok": "Драйверы для {} установлены",
    "gpu_nvidia_config": "Конфигурация NVIDIA создана",
    "gpu_nvidia_mkinit": "NVIDIA добавлена в mkinitcpio",

    "error_pm": "Не удалось определить менеджер пакетов!",
    "error_not_arch": "Это не Arch Linux!",
    "error_root": "Запустите с sudo: sudo dpa {}",
    "error_mount": "{} не является точкой монтирования",
    "error_mount_help": "Сначала смонтируйте корневой раздел: mount /dev/sdXN {}",

    "alias_added": "Алиас добавлен: {} -> {}",
    "alias_add_help": "Добавьте алиас: dpa alias add --alias <имя> --real <пакет>",

    "uninstalling": "Удаление DPA...",

    "uninstalled": "DPA успешно удалён",

    "uninstall_removed": "  Удалён: {}",
    "uninstall_dir": "  Удалена директория: {}",
    "uninstall_warn": "  Предупреждение: Не удалось удалить {}: {}",

    "interrupt": "\nПрервано пользователем",

    "banner_tagline": "Универсальный менеджер пакетов",

    "desc": "DPA - Универсальный менеджер пакетов",

    "grp_packages": "Пакеты",
    "grp_tools": "Инструменты",
    "grp_arch": "Arch Linux",
    "grp_options": "Опции",

    "overview_hint": "Подробнее: dpa <команда> --help   |   Предпросмотр без изменений: --dry-run",

    "help_install": "Установить пакет(ы)",
    "help_remove": "Удалить пакет(ы)",
    "help_update": "Обновить сведения о пакетах / показать обновления",
    "help_upgrade": "Обновить систему",
    "help_search": "Поиск пакетов",
    "help_info": "Информация о пакете",
    "help_list": "Список установленных пакетов",
    "help_clean": "Очистить кеш пакетов",
    "help_autoremove": "Удалить ненужные пакеты",
    "help_history": "История транзакций",
    "help_alias": "Управление алиасами пакетов",
    "help_distro": "Информация о системе",
    "help_lang": "Показать или сменить язык",
    "help_completion": "Автодополнение для оболочки",
    "help_uninstall": "Удалить DPA",
    "help_arch_install": "Установка базового Arch Linux (pacstrap)",
    "help_arch_config": "Настройка Arch: локаль, пользователи, загрузчик",
    "help_arch_desktop": "Установка графического окружения",
    "help_arch_server": "Установка серверного окружения",
    "help_arch_dev": "Установка окружения разработчика",
    "help_arch_gaming": "Установка игрового окружения",

    "opt_yes": "Не задавать вопросов",
    "opt_dry_run": "Показать команды, не выполняя их",
    "opt_no_color": "Отключить цвета",
    "opt_version": "Показать версию",
    "opt_help": "Показать справку",
    "opt_limit": "Сколько записей показать",
    "opt_alias_name": "Имя алиаса",
    "opt_alias_real": "Реальное имя пакета",
    "opt_comp_install": "Установить автодополнение для ваших оболочек",
    "opt_keep_data": "Оставить историю и алиасы",
    "opt_target": "Целевая директория (по умолчанию: /mnt)",
    "opt_target_auto": "Целевая директория (по умолчанию: /mnt, если смонтирован, иначе /)",
    "opt_extra_packages": "Дополнительные пакеты",
    "opt_de": "Графическое окружение (по умолчанию: gnome)",
    "opt_no_gpu": "Не устанавливать драйверы видеокарты",
    "opt_services": "Категории для установки ({}); пропускает вопрос",
    "opt_user": "Существующий пользователь в целевой системе",

    "dry_run_banner": "Пробный запуск: ничего не будет изменено",
    "dry_write": "запись файла {}",

    "write_failed": "Не удалось записать {}: {}",

    "db_unavailable": "История и пользовательские алиасы недоступны: {}",

    "cmd_failed": "Команда завершилась с кодом {}",
    "cmd_not_found": "Команда не найдена: {}",

    "error_no_sudo": "sudo/doas не найдены - запустите dpa от root",

    "invalid_package": "Недопустимое имя пакета: {}",

    "pkg_not_found": "Пакет не найден: {}",

    "no_matches": "Ничего не найдено",

    "nothing_to_remove": "Ненужных пакетов нет",

    "orphans_found": "Ненужные пакеты: {}",

    "pacman_refresh_note": "В Arch база пакетов синхронизируется вместе с обновлением. Выполните: dpa upgrade (для просмотра обновлений поставьте pacman-contrib)",

    "alias_resolved": "Алиас: {} -> {} ({})",
    "alias_custom_resolved": "Свой алиас: {} -> {} ({})",
    "alias_title": "Алиасы пакетов ({})",
    "alias_removed": "Алиас удалён: {}",
    "alias_not_found": "Алиас не найден: {}",
    "alias_need_args": "Использование: dpa alias add <имя> <пакет>  |  dpa alias remove <имя>",
    "alias_type_builtin": "встроенный",
    "alias_type_custom": "свой",

    "col_alias": "Алиас",
    "col_package": "Пакет",
    "col_type": "Тип",
    "col_time": "Время",
    "col_command": "Команда",
    "col_packages": "Пакеты",
    "col_category": "Категория",

    "lbl_distribution": "Дистрибутив",
    "lbl_pm": "Менеджер пакетов",
    "lbl_kernel": "Ядро",
    "lbl_arch": "Архитектура",
    "lbl_python": "Python",
    "lbl_dpa": "DPA",
    "lbl_language": "Язык",
    "lbl_config": "Конфиг",
    "lbl_data": "Данные",
    "lbl_cache": "Кеш",
    "lbl_backend": "бэкенд",

    "lang_available": "Доступны",
    "lang_set": "Язык установлен: {}",

    "completion_installed": "Автодополнение установлено: {}",
    "completion_reload": "Перезапустите оболочку, чтобы оно заработало",
    "completion_none": "Поддерживаемые оболочки не найдены",

    "yn_yes_default": "[Д/н]",
    "yn_no_default": "[д/Н]",

    "confirm_noninteractive": "Нет терминала для вопроса - берём ответ по умолчанию (используйте --yes)",

    "cancelled": "Отменено",

    "uninstall_confirm": "Удалить DPA и его файлы?",
    "uninstall_hint_remove": "'uninstall' удаляет сам DPA. Чтобы удалить пакет: dpa remove <пакет>",

    "installing_pkgs": "pacman: {}",

    "error_tools": "Не найдены нужные утилиты: {} (pacman -S arch-install-scripts)",
    "error_no_base": "В {} нет базовой системы - сначала выполните: sudo dpa arch-install",

    "arch_install_fstab_fail": "genfstab не сработал - смонтирован ли целевой раздел?",
    "arch_multilib": "Включаю репозиторий multilib",
    "arch_service_enabled": "Сервис включён: {}",
    "arch_need_config": "До первой загрузки задайте пароли/пользователей: sudo dpa arch-config",
    "arch_desktop_start": "Менеджера входа нет. Запуск сессии: {}",
    "arch_dev_no_user": "AUR-помощник (yay) пропущен: укажите --user <имя> существующего пользователя",
    "arch_user_missing": "Пользователя '{}' нет в целевой системе - создайте его через dpa arch-config",
    "arch_server_web_conflict": "nginx и apache занимают порт 80 - включу только nginx",
    "arch_config_target": "Целевая система: {}",
    "arch_config_enter_locale": "Локали (через пробел)",
    "arch_config_enter_tz": "Часовой пояс",
    "arch_config_enter_keymap": "Раскладка консоли",
    "arch_config_bad_tz": "Неизвестный часовой пояс: {}",
    "arch_config_bad_user": "Недопустимое имя пользователя: {}",
    "arch_config_no_grub": "GRUB в целевой системе не установлен - загрузчик пропускаем",
    "arch_config_sudo_bad": "Проверка sudoers не прошла - правило sudo удалено",

    "gpu_nvidia_legacy": "Эта видеокарта NVIDIA не поддерживается nvidia-open. Ставлю mesa (nouveau); старые драйверы есть в AUR",
}
