# -*- mode: python -*-
a = Analysis(['zchat_server.py'],
             pathex=['F:\\workplace\\Python\\network-study\\zchat'],
             hiddenimports=['zope.interface'],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\zchat_server', 'zchat_server.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'zchat_server'))
