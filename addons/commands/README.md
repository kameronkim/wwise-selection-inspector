# Wwise Command Add-on

This folder contains user-level Command Add-on installers for Wwise Selection Inspector.

The recommended setup is a common user-level add-on, not a project-level add-on.

```text
addons/commands/user/install_macos.command
addons/commands/user/install_windows.ps1
addons/commands/user/README.md
```

The installer writes the command definition to the user's Wwise add-on directory:

```text
macOS:
$HOME/Library/Application Support/Audiokinetic/Wwise/Add-ons/Commands

Windows:
%APPDATA%\Audiokinetic\Wwise\Add-ons\Commands
```

This makes the command available across Wwise projects for that user.

The command appears in Wwise as:

```text
Tools > Wwise Selection Inspector > Open Wwise Selection Inspector
```

It is also available from the context menu as:

```text
Wwise Selection Inspector > Open Wwise Selection Inspector
```

See `addons/commands/user/README.md` for install steps.
