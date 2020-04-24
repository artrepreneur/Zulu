import os, sys
from PyQt5.QtGui import *
#from resource import resource_path

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def set_pixmaps():
    # Pixmap Imgs
    global pixmap_balance_btn, pixmap_balance_btn2, pixmap_addr_btn, pixmap_addr_btn2
    global icons, pixmap_send_btn, pixmap_send_btn2, pixmap_receive_btn, pixmap_receive_btn2, pixmap_transaction_btn, pixmap_transaction_btn2
    pixmap_addr_btn = QPixmap(resource_path('img/glyphicons_325_wallet_blk@2x.png'))
    pixmap_addr_btn2 = QPixmap(resource_path('img/glyphicons_325_wallet_blk_alt@2x.png'))
    pixmap_balance_btn = QPixmap(resource_path('img/glyphicons_325_wallet@2x.png'))
    pixmap_balance_btn2 = QPixmap(resource_path('img/glyphicons_325_wallet_alt@2x.png'))
    pixmap_send_btn = QPixmap(resource_path('img/glyphicons_222_share@2x.png'))
    pixmap_send_btn2 = QPixmap(resource_path('img/glyphicons_222_share_alt@2x.png'))
    pixmap_receive_btn = QPixmap(resource_path('img/glyphicons_221_unshare@2x.png'))
    pixmap_receive_btn2 = QPixmap(resource_path('img/glyphicons_221_unshare_alt@2x.png'))
    pixmap_transaction_btn = QPixmap(resource_path('img/glyphicons_457_transfer@2x.png'))
    pixmap_transaction_btn2 = QPixmap(resource_path('img/glyphicons_457_transfer_alt@2x.png'))
    icons = {'pixmap_addr_btn':pixmap_addr_btn, 'pixmap_addr_btn2':pixmap_addr_btn2, 'pixmap_balance_btn': pixmap_balance_btn, 'pixmap_balance_btn2':pixmap_balance_btn2, 'pixmap_send_btn':pixmap_send_btn, 'pixmap_send_btn2':pixmap_send_btn2, 'pixmap_receive_btn':pixmap_receive_btn, 'pixmap_receive_btn2':pixmap_receive_btn2,'pixmap_transaction_btn':pixmap_transaction_btn,'pixmap_transaction_btn2':pixmap_transaction_btn2}
    return icons
