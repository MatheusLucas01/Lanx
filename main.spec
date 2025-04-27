# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['src/main.py'],
             # ADICIONA 'src' AO PATHEX JUNTO COM '.' (RAIZ)
             pathex=['.', 'src'],
             binaries=[],
             datas=[
                 ('products.json', '.'),
                 ('vendas.json', '.'),
                 ('src/assets', 'assets')
             ],
             # MANTÉM OS HIDDEN IMPORTS (config e ui)
             hiddenimports=['config', 'ui'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher_block_size=16,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

# A seção EXE geralmente é gerada corretamente por pyi-makespec
# Apenas garanta que 'console=False' está lá se você usou --noconsole
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas, # Garante que datas está aqui
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, # <--- Garanta que está False
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
# A seção COLLECT também deve estar OK
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
