# User-level Wwise Command Add-on

Wwise Selection Inspector can be launched from Wwise as a user-level Command Add-on.

This does not dock the inspector inside Wwise. It adds a Wwise menu/context-menu command that opens the packaged companion app.

## Recommended install model

Install once per user, not per Wwise project.

```text
Application:
- macOS: /Applications/Wwise Selection Inspector.app
- Windows: packaged WwiseSelectionInspector folder, usually under a user or tools directory

Command Add-on:
- macOS: $HOME/Library/Application Support/Audiokinetic/Wwise/Add-ons/Commands
- Windows: %APPDATA%\Audiokinetic\Wwise\Add-ons\Commands
```

After this, the command is available across Wwise projects for that user.

## macOS install

1. Copy `Wwise Selection Inspector.app` to `/Applications`.
2. Run `install_macos.command`.
3. Restart Wwise.
4. Run the command from:

```text
Tools > Wwise Selection Inspector > Open Wwise Selection Inspector
```

If the app is installed somewhere other than `/Applications`, run:

```bash
./install_macos.command "/path/to/any-app-name.app"
```

## Windows install

1. Extract the packaged `WwiseSelectionInspector` folder.
2. Run PowerShell from that folder.
3. Run:

```powershell
.\install_windows.ps1
```

If the executable is installed somewhere else, run:

```powershell
.\install_windows.ps1 -AppPath "C:\Path\To\WwiseSelectionInspector.exe"
```

Restart Wwise, then run:

```text
Tools > Wwise Selection Inspector > Open Wwise Selection Inspector
```

## Context menu

The command is also available from the Wwise context menu as:

```text
Wwise Selection Inspector > Open Wwise Selection Inspector
```

## Notes

- Do not install this into each Wwise project unless project-specific distribution is required.
- The generated command file contains an absolute path to the packaged app.
- If the app is moved, run the installer again.
- Wwise Authoring API must still be enabled for the inspector to read the current selection.


## macOS app path notes

The macOS installer accepts any valid `.app` bundle name. The bundle does not have to be named `Wwise Selection Inspector.app`; the script resolves the executable inside `Contents/MacOS`.

Example:

```bash
./install_macos.command "/Users/ziwon/Downloads/1.app"
```
