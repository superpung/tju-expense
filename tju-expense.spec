# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
asset_name = os.getenv('ASSET_NAME', 'tju-expense')

a = Analysis(
    ['src/tju_expense/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('src/tju_expense/LXGWWenKaiLite-Regular.ttf', 'tju_expense')],
    hiddenimports=[],
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
    name=asset_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
