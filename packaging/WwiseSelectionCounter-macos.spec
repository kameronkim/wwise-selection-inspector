# PyInstaller spec for macOS .app distribution.
from pathlib import Path
import os

# PyInstaller does not always define __file__ while executing a spec.
# The build scripts set WSC_PROJECT_ROOT explicitly; SPECPATH is used as a fallback.
project_root = Path(os.environ.get("WSC_PROJECT_ROOT", Path(SPECPATH).resolve().parent)).resolve()

block_cipher = None

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=["waapi"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WwiseSelectionCounter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WwiseSelectionCounter",
)

app = BUNDLE(
    coll,
    name="Wwise Selection Counter.app",
    icon=None,
    bundle_identifier="com.kameron.wwise-selection-counter",
    info_plist={
        "CFBundleDisplayName": "Wwise Selection Counter",
        "CFBundleName": "Wwise Selection Counter",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
    },
)
