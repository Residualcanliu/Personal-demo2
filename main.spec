# -*- mode: python ; coding: utf-8 -*-
import os
import akshare

akshare_path = os.path.dirname(akshare.__file__)
file_fold_src = os.path.join(akshare_path, 'file_fold')
file_fold_dst = 'akshare/file_fold'       

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),         
        ('fonts', 'fonts'),                 
        (file_fold_src, file_fold_dst)      
    ],
    hiddenimports=['nodejs_bin'],        
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='智能企业融资风险中控服务系统',
    icon='resources/app.ico',
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