# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(['PKTWallet.py'],
             binaries=[
               ('build/deps/libzbar.dylib', '.'),
               ('build/deps/jpeg/9d/lib/libjpeg.9.dylib','.')
             ],
             datas=[
               ('QRCodes', 'QRCodes')
             ],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('img/glyphicons_325_wallet_blk@2x.png', 'img/glyphicons_325_wallet_blk@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet_blk_alt@2x.png', 'img/glyphicons_325_wallet_blk_alt@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet@2x.png', 'img/glyphicons_325_wallet@2x.png', 'DATA'),
         ('img/glyphicons_325_wallet_alt@2x.png', 'img/glyphicons_325_wallet_alt@2x.png', 'DATA'),
         ('img/glyphicons_222_share@2x.png', 'img/glyphicons_222_share@2x.png', 'DATA'),
         ('img/glyphicons_222_share_alt@2x.png', 'img/glyphicons_222_share_alt@2x.png', 'DATA'),
         ('img/glyphicons_221_unshare@2x.png', 'img/glyphicons_221_unshare@2x.png', 'DATA'),
         ('img/glyphicons_221_unshare_alt@2x.png', 'img/glyphicons_221_unshare_alt@2x.png', 'DATA'),
         ('img/glyphicons_457_transfer@2x.png', 'img/glyphicons_457_transfer@2x.png', 'DATA'),
         ('img/glyphicons_457_transfer_alt@2x.png', 'img/glyphicons_457_transfer_alt@2x.png', 'DATA'),
         ('img/glyphicons_051_eye_open.png', 'img/glyphicons_051_eye_open.png', 'DATA'),
         ('img/glyphicons_052_eye_close.png', 'img/glyphicons_052_eye_close.png', 'DATA'),
         ('img/glyphicons_081_refresh@2x.png', 'img/glyphicons_081_refresh@2x.png', 'DATA'),
         ('img/glyphicons_081_refresh_alt@2x.png', 'img/glyphicons_081_refresh_alt@2x.png', 'DATA'),
         ('img/app_icon.png', 'img/app_icon.png', 'DATA'),
         ('img/PKT.iconset/icon_1024x1024@2x.png','img/PKT.iconset/icon_1024x1024@2x.png', 'DATA'),
         ('img/grn_btn.png','img/grn_btn.png', 'DATA'),
         ('img/red_btn.png','img/red_btn.png', 'DATA'),
         ('img/ylw_btn.png','img/ylw_btn.png', 'DATA'),
         ('MultisigData/mdata.json', 'MultisigData/mdata.json', 'DATA'),
         ('bin/pktd', 'bin/pktd', 'DATA'),
         ('bin/pktctl', 'bin/pktctl', 'DATA'),
         ('bin/wallet', 'bin/wallet', 'DATA'),
         ('bin/getwalletdb', 'bin/getwalletdb', 'DATA'),
         ('img/glyphicons_325_wallet_blk_alt@2x.png', 'img/glyphicons_325_wallet_blk_alt@2x.png', 'DATA')]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if sys.platform == 'darwin':
     exe = EXE(pyz,
               a.scripts,
               a.binaries,
               a.zipfiles,
               a.datas,
               name='PKTWallet',
               debug=True,
               strip=False,
               upx=True,
               runtime_tmpdir=None,
               console=True,
               icon='img/PKT.icns')

# Package the executable file into .app if on OS X
if sys.platform == 'darwin':
      app = BUNDLE(exe,
                   name='PKTWallet.app',
                   info_plist={
                     'NSHighResolutionCapable': 'True',
                     'LSBackgroundOnly': '1',
                     'LSBackgroundOnly': 'False'
                   },
                   icon='img/PKT.icns')

coll = COLLECT(exe,
             a.binaries,
             a.zipfiles,
             a.datas,
             strip=False,
             upx=True,
             upx_exclude=[],
             name='PKTWallet')
