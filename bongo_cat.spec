# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Bongo Cat."""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
APP_NAME = 'BongoCat'
APP_ICON = 'img/cat-rest.png' if os.path.exists('img/cat-rest.png') else None
IS_MACOS = sys.platform == 'darwin'


def app_version():
    """Return the release tag version when available, otherwise package version."""
    ref_name = os.environ.get('GITHUB_REF_NAME', '')
    if ref_name.startswith('v') and ref_name[1:]:
        return ref_name[1:]

    try:
        from bongo_cat import __version__
        return __version__
    except Exception:
        return '0.0.0'


APP_VERSION = app_version()

# Collect all data files
datas = []

# Add required directories
if os.path.exists('img'):
    datas += [('img', 'img')]
if os.path.exists('skins'):
    datas += [('skins', 'skins')]

# Add optional directories (sound effects are optional)
if os.path.exists('sounds'):
    datas += [('sounds', 'sounds')]

# Add config file if it exists
if os.path.exists('bongo.ini'):
    datas += [('bongo.ini', '.')]

# Collect PyQt5 data files
datas += collect_data_files('PyQt5')

# Collect hidden imports
hiddenimports = []
hiddenimports += collect_submodules('PyQt5')
hiddenimports += ['pynput.keyboard', 'pynput.mouse', 'pygame', 'pygame.mixer']

# pynput selects these dynamically; headless CI cannot discover them by import.
if sys.platform.startswith('linux'):
    hiddenimports += ['pynput.keyboard._xorg', 'pynput.mouse._xorg']

a = Analysis(
    ['bongo_cat/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [] if IS_MACOS else a.binaries,
    [] if IS_MACOS else a.zipfiles,
    [] if IS_MACOS else a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=not IS_MACOS,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=APP_ICON,
    exclude_binaries=IS_MACOS,
)

# macOS app bundle
if IS_MACOS:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name=APP_NAME,
    )

    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=APP_ICON,
        bundle_identifier='com.luinbytes.bongocat',
        version=APP_VERSION,
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleVersion': APP_VERSION,
        },
    )
