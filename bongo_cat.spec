# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Bongo Cat."""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files
datas = []
datas += [('img', 'img')]
datas += [('skins', 'skins')]
datas += [('sounds', 'sounds')]
datas += [('bongo.ini', '.')]

# Collect PyQt5 data files
datas += collect_data_files('PyQt5')

# Collect hidden imports
hiddenimports = []
hiddenimports += collect_submodules('PyQt5')
hiddenimports += ['pynput.keyboard', 'pynput.mouse', 'pygame', 'pygame.mixer']

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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BongoCat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='img/cat-rest.png' if os.path.exists('img/cat-rest.png') else None,
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='BongoCat.app',
        icon='img/cat-rest.png' if os.path.exists('img/cat-rest.png') else None,
        bundle_identifier='com.luinbytes.bongocat',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
        },
    )
