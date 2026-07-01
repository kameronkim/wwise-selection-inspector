# PyInstaller spec for macOS .app distribution.
from pathlib import Path
import os

project_root = Path(os.environ.get("WSI_PROJECT_ROOT", Path(SPECPATH).resolve().parent)).resolve()

block_cipher = None

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=["waapi", "PySide6.QtNetwork"],
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
    name="WwiseSelectionInspector",
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
    name="WwiseSelectionInspector",
)

app = BUNDLE(
    coll,
    name="Wwise Selection Inspector.app",
    icon=None,
    bundle_identifier="com.kameron.wwise-selection-inspector",
    info_plist={
        "CFBundleDisplayName": "Wwise Selection Inspector",
        "CFBundleName": "Wwise Selection Inspector",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
    },
)
