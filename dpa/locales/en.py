"""Строки интерфейса (en)."""
from __future__ import annotations

STRINGS = {
    "installing": "Installing: {}",

    "removing": "Removing: {}",

    "updating": "Updating package list",

    "upgrading": "Upgrading system",

    "searching": "Searching: {}",

    "info_pkg": "Package info: {}",

    "listing": "Listing installed packages",

    "cleaning": "Cleaning package cache",

    "autoremoving": "Removing unused packages",

    "completed": "Installation completed: {} package(s)",

    "removed": "Removal completed: {} package(s)",

    "updated": "Package list updated",

    "upgraded": "System upgraded",

    "cleaned": "Cache cleaned",

    "autoremoved": "Unused packages removed",

    "failed": "Operation failed",

    "history_title": "Transaction history (last {})",
    "history_empty": "History is empty",

    "distro_title": "System information",

    "arch_install_title": "Arch Linux Installation",
    "arch_install_base": "Installing base system...",
    "arch_install_fstab": "Generating fstab...",
    "arch_install_config": "Configuring system...",
    "arch_install_ok": "Arch Linux installed successfully",
    "arch_install_path": "  System installed to: {}",
    "arch_install_next": "Next steps:",
    "arch_install_step1": "  1. Configure the system: sudo dpa arch-config --target {}",
    "arch_install_step2": "  2. Optional: sudo dpa arch-desktop --de gnome",
    "arch_install_step3": "  3. Unmount (umount -R /mnt) and reboot",
    "arch_config_title": "Arch Linux Configuration",
    "arch_config_locale": "Configuring locale...",
    "arch_config_hostname": "Setting hostname...",
    "arch_config_enter_host": "Hostname",
    "arch_config_root_pw": "Setting root password...",
    "arch_config_user": "Creating user...",
    "arch_config_create": "Create a user?",
    "arch_config_username": "Username",
    "arch_config_set_pw": "Set password for {}",
    "arch_config_user_ok": "User {} created",
    "arch_config_boot": "Installing bootloader...",
    "arch_config_boot_mode": "Boot mode (uefi/bios)",
    "arch_config_disk": "Disk (e.g. /dev/sda)",
    "arch_config_skip": "Skipping bootloader installation",
    "arch_config_ok": "Configuration completed",
    "arch_config_exit": "Unmount (umount -R /mnt) and reboot",
    "arch_desktop_title": "Installing {}",
    "arch_desktop_not_found": "Environment '{}' not found!",
    "arch_desktop_available": "Available environments:",
    "arch_desktop_example": "Example: dpa arch-desktop --de gnome",
    "arch_desktop_packages": "Installing packages: {}",
    "arch_desktop_gpu": "Detecting and installing GPU drivers...",
    "arch_desktop_ok": "{} installed",
    "arch_desktop_reboot": "Reboot and login to your system",
    "arch_server_title": "Arch Linux Server Environment",
    "arch_server_available": "Available services:",
    "arch_server_enter": "Enter category names or numbers (space separated), or Enter for defaults:",
    "arch_server_default": "Default: web, database, devops",
    "arch_server_unknown": "Unknown service: {}",
    "arch_server_none": "No packages to install",
    "arch_server_install": "Installing: {}",
    "arch_server_ok": "Server environment installed",
    "arch_server_complete": "To complete setup:",
    "arch_dev_title": "Arch Linux Development Environment",
    "arch_dev_install": "Installing developer packages...",
    "arch_dev_aur": "Installing AUR helper (yay)...",
    "arch_dev_ok": "Development environment installed",
    "arch_dev_extra": "Additional steps:",
    "arch_gaming_title": "Arch Linux Gaming Environment",
    "arch_gaming_install": "Installing gaming packages...",
    "arch_gaming_ok": "Gaming environment installed",
    "arch_gaming_list": "  Installed:",

    "gpu_detecting": "Detecting GPU...",
    "gpu_unknown": "Unable to detect GPU. Skipping drivers.",
    "gpu_detected": "  Detected: {}",
    "gpu_vendor": "  Vendor: {}",
    "gpu_failed": "Failed to install drivers for {}",
    "gpu_ok": "Drivers for {} installed",
    "gpu_nvidia_config": "NVIDIA configuration created",
    "gpu_nvidia_mkinit": "NVIDIA added to mkinitcpio",

    "error_pm": "Unable to detect package manager!",
    "error_not_arch": "This is not Arch Linux!",
    "error_root": "Run with sudo: sudo dpa {}",
    "error_mount": "{} is not a mount point",
    "error_mount_help": "Mount the root partition first: mount /dev/sdXN {}",

    "alias_added": "Alias added: {} -> {}",
    "alias_add_help": "Add custom alias: dpa alias add --alias <name> --real <package>",

    "uninstalling": "Removing DPA...",

    "uninstalled": "DPA removed successfully",

    "uninstall_removed": "  Removed: {}",
    "uninstall_dir": "  Removed directory: {}",
    "uninstall_warn": "  Warning: Could not remove {}: {}",

    "interrupt": "\nInterrupted by user",

    "banner_tagline": "Universal package manager",

    "desc": "DPA - Universal Package Manager",

    "grp_packages": "Packages",
    "grp_tools": "Tools",
    "grp_arch": "Arch Linux",
    "grp_options": "Options",

    "overview_hint": "Details: dpa <command> --help   |   Preview without changes: --dry-run",

    "help_install": "Install package(s)",
    "help_remove": "Remove package(s)",
    "help_update": "Refresh package info / show updates",
    "help_upgrade": "Upgrade the system",
    "help_search": "Search packages",
    "help_info": "Show package information",
    "help_list": "List installed packages",
    "help_clean": "Clean package cache",
    "help_autoremove": "Remove unused packages",
    "help_history": "Transaction history",
    "help_alias": "Manage package aliases",
    "help_distro": "System information",
    "help_lang": "Show or change the language",
    "help_completion": "Shell completion",
    "help_uninstall": "Uninstall DPA",
    "help_arch_install": "Install base Arch Linux (pacstrap)",
    "help_arch_config": "Configure Arch: locale, users, bootloader",
    "help_arch_desktop": "Install a desktop environment",
    "help_arch_server": "Install a server environment",
    "help_arch_dev": "Install a developer environment",
    "help_arch_gaming": "Install a gaming environment",

    "opt_yes": "Do not ask for confirmation",
    "opt_dry_run": "Show commands without running them",
    "opt_no_color": "Disable colours",
    "opt_version": "Show version",
    "opt_help": "Show help",
    "opt_limit": "How many entries to show",
    "opt_alias_name": "Alias name",
    "opt_alias_real": "Real package name",
    "opt_comp_install": "Install completion for your shells",
    "opt_keep_data": "Keep history and aliases",
    "opt_target": "Target directory (default: /mnt)",
    "opt_target_auto": "Target directory (default: /mnt if mounted, else /)",
    "opt_extra_packages": "Additional packages",
    "opt_de": "Desktop environment (default: gnome)",
    "opt_no_gpu": "Skip GPU driver installation",
    "opt_services": "Categories to install ({}); skips the prompt",
    "opt_user": "Existing user in the target system",

    "dry_run_banner": "Dry run: nothing will be changed",
    "dry_write": "write file {}",

    "write_failed": "Could not write {}: {}",

    "db_unavailable": "History and custom aliases are unavailable: {}",

    "cmd_failed": "Command failed with exit code {}",
    "cmd_not_found": "Command not found: {}",

    "error_no_sudo": "sudo/doas not found - run dpa as root",

    "invalid_package": "Invalid package name: {}",

    "pkg_not_found": "Package not found: {}",

    "no_matches": "Nothing found",

    "nothing_to_remove": "No unused packages",

    "orphans_found": "Unused packages: {}",

    "pacman_refresh_note": "On Arch the package database is synced together with the upgrade. Run: dpa upgrade (install pacman-contrib to preview updates)",

    "alias_resolved": "Alias: {} -> {} ({})",
    "alias_custom_resolved": "Custom alias: {} -> {} ({})",
    "alias_title": "Package aliases ({})",
    "alias_removed": "Alias removed: {}",
    "alias_not_found": "Alias not found: {}",
    "alias_need_args": "Usage: dpa alias add <name> <package>  |  dpa alias remove <name>",
    "alias_type_builtin": "built-in",
    "alias_type_custom": "custom",

    "col_alias": "Alias",
    "col_package": "Package",
    "col_type": "Type",
    "col_time": "Time",
    "col_command": "Command",
    "col_packages": "Packages",
    "col_category": "Category",

    "lbl_distribution": "Distribution",
    "lbl_pm": "Package manager",
    "lbl_kernel": "Kernel",
    "lbl_arch": "Architecture",
    "lbl_python": "Python",
    "lbl_dpa": "DPA",
    "lbl_language": "Language",
    "lbl_config": "Config",
    "lbl_data": "Data",
    "lbl_cache": "Cache",
    "lbl_backend": "backend",

    "lang_available": "Available",
    "lang_set": "Language set: {}",

    "completion_installed": "Completion installed: {}",
    "completion_reload": "Restart your shell to enable it",
    "completion_none": "No supported shells found",

    "yn_yes_default": "[Y/n]",
    "yn_no_default": "[y/N]",

    "confirm_noninteractive": "No terminal for a question - using the default answer (use --yes)",

    "cancelled": "Cancelled",

    "uninstall_confirm": "Remove DPA and its files?",
    "uninstall_hint_remove": "'uninstall' removes DPA itself. To remove a package use: dpa remove <package>",

    "installing_pkgs": "pacman: {}",

    "error_tools": "Required tools not found: {} (pacman -S arch-install-scripts)",
    "error_no_base": "No base system in {} - run first: sudo dpa arch-install",

    "arch_install_fstab_fail": "genfstab failed - is the target mounted?",
    "arch_multilib": "Enabling the multilib repository",
    "arch_service_enabled": "Service enabled: {}",
    "arch_need_config": "Before the first boot set passwords/users: sudo dpa arch-config",
    "arch_desktop_start": "No display manager. Start the session with: {}",
    "arch_dev_no_user": "AUR helper (yay) skipped: pass --user <name> of an existing user",
    "arch_user_missing": "User '{}' does not exist in the target system - create it with dpa arch-config",
    "arch_server_web_conflict": "nginx and apache both use port 80 - only nginx will be enabled",
    "arch_config_target": "Target system: {}",
    "arch_config_enter_locale": "Locales (space separated)",
    "arch_config_enter_tz": "Time zone",
    "arch_config_enter_keymap": "Console keymap",
    "arch_config_bad_tz": "Unknown time zone: {}",
    "arch_config_bad_user": "Invalid user name: {}",
    "arch_config_no_grub": "GRUB is not installed in the target - skipping bootloader",
    "arch_config_sudo_bad": "sudoers check failed - sudo rule removed",

    "gpu_nvidia_legacy": "This NVIDIA GPU is not supported by nvidia-open. Installing mesa (nouveau); legacy drivers are available from the AUR",
}
