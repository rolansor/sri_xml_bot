# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

# Other PyInstaller imports
from PyInstaller.utils.hooks import collect_submodules

# Collect all submodules for reportlab
hiddenimports = collect_submodules('reportlab')

a = Analysis(
    ['sri_xml_bot\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('archivos_necesarios/rucs.txt', 'archivos_necesarios'),
        ('archivos_necesarios/credenciales_rucs.txt', 'archivos_necesarios'),
        ('archivos_necesarios/chromedriver.exe', 'archivos_necesarios'),
        ('archivos_necesarios/nologo.png', 'archivos_necesarios'),
    ],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

#correr el script
#pyinstaller main.spec