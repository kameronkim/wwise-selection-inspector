#!/bin/bash
set -euo pipefail

DEFAULT_APP_BUNDLE="/Applications/Wwise Selection Inspector.app"
INPUT_PATH="${1:-$DEFAULT_APP_BUNDLE}"
COMMAND_DIR="$HOME/Library/Application Support/Audiokinetic/Wwise/Add-ons/Commands"
COMMAND_FILE="$COMMAND_DIR/kameron_wwise_selection_inspector.json"

resolve_executable() {
  local path="$1"

  if [ -d "$path" ]; then
    if [[ "$path" != *.app ]]; then
      echo "ERROR_NOT_APP_DIR:$path"
      return 1
    fi

    local macos_dir="$path/Contents/MacOS"

    if [ ! -d "$macos_dir" ]; then
      echo "ERROR_INVALID_APP:$path"
      return 1
    fi

    local preferred="$macos_dir/WwiseSelectionInspector"
    if [ -x "$preferred" ]; then
      echo "$preferred"
      return 0
    fi

    local executable
    executable=$(find "$macos_dir" -maxdepth 1 -type f -perm -111 | head -n 1 || true)

    if [ -n "$executable" ]; then
      echo "$executable"
      return 0
    fi

    echo "ERROR_NO_EXECUTABLE:$path"
    return 1
  fi

  if [ -f "$path" ] && [ -x "$path" ]; then
    echo "$path"
    return 0
  fi

  echo "ERROR_NOT_FOUND:$path"
  return 1
}

APP_EXECUTABLE_RESULT=$(resolve_executable "$INPUT_PATH" || true)

case "$APP_EXECUTABLE_RESULT" in
  ERROR_NOT_FOUND:*)
    cat <<MESSAGE
Wwise Selection Inspector app was not found at:
$INPUT_PATH

Pass the actual .app bundle path, for example:
$(basename "$0") "/Users/ziwon/Downloads/Wwise Selection Inspector.app"

You can find app bundles with:
find ~/Downloads -maxdepth 3 -name "*.app" -print
MESSAGE
    exit 1
    ;;
  ERROR_NOT_APP_DIR:*)
    cat <<MESSAGE
The provided path exists but is not a macOS .app bundle:
$INPUT_PATH

Pass a .app bundle path or an executable inside a .app bundle.
MESSAGE
    exit 1
    ;;
  ERROR_INVALID_APP:*)
    cat <<MESSAGE
Invalid macOS app bundle:
$INPUT_PATH

The bundle is missing Contents/MacOS.
MESSAGE
    exit 1
    ;;
  ERROR_NO_EXECUTABLE:*)
    cat <<MESSAGE
No executable file was found inside:
$INPUT_PATH/Contents/MacOS

Make sure this is the packaged Wwise Selection Inspector app.
MESSAGE
    exit 1
    ;;
esac

APP_EXECUTABLE="$APP_EXECUTABLE_RESULT"
APP_CWD="$(dirname "$APP_EXECUTABLE")"

mkdir -p "$COMMAND_DIR"

APP_EXECUTABLE_ESCAPED=$(printf '%s' "$APP_EXECUTABLE" | sed 's/[\\"]/\\&/g')
APP_CWD_ESCAPED=$(printf '%s' "$APP_CWD" | sed 's/[\\"]/\\&/g')

cat > "$COMMAND_FILE" <<JSON
{
  "version": 2,
  "commands": [
    {
      "id": "kameron.wwise-selection-inspector.open",
      "displayName": "Open Wwise Selection Inspector",
      "program": "$APP_EXECUTABLE_ESCAPED",
      "args": "",
      "cwd": "$APP_CWD_ESCAPED",
      "startMode": "MultipleSelectionSingleProcessSpaceSeparated",
      "contextMenu": {
        "basePath": "Wwise Selection Inspector"
      },
      "mainMenu": {
        "basePath": "Tools/Wwise Selection Inspector"
      }
    }
  ]
}
JSON

cat <<MESSAGE
Installed Wwise Selection Inspector command add-on:
$COMMAND_FILE

Resolved app executable:
$APP_EXECUTABLE

Restart Wwise, then run:
Tools > Wwise Selection Inspector > Open Wwise Selection Inspector
MESSAGE
