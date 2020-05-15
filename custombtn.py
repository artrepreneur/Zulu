# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize
from pixMp import *

# Dynamic button class
class BasicBtn (QtWidgets.QPushButton):
    def __init__(self, obj_name, obj_text, bl, *args, **kwargs):
        super(BasicBtn, self).__init__(*args, **kwargs)

        #global icons, bal
        self.bal = bl
        self.icons = set_pixmaps() #-- must construct QApplication First
        self.text = obj_text
        self.name = obj_name

        self.setText(self.text)
        #pixmap_addr_btn = QPixmap(resource_path('img/glyphicons_325_wallet_blk@2x.png'))
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icons['pixmap_addr_btn']))
        self.setIconSize(QSize(70,40))
        self.setStyleSheet("QPushButton#"+self.name+"{border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 20pt 'Futura'; text-align: center}")

    def mousePressEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icons['pixmap_addr_btn2']))
        self.setIconSize(QSize(70,40))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 5px; border: 1px solid #FF6600; font: 57 20pt 'Futura'; text-align: center; color: #FF6600; background-color: #022D93;}")

    def mouseReleaseEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icons['pixmap_addr_btn']))
        self.setIconSize(QSize(70,40))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 20pt 'Futura'; text-align: center;}")
        btn_click_handler(self)

class ListBtn(BasicBtn):
    #set_pixmaps() #-- must construct QApplication First
    def mouseReleaseEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icons['pixmap_addr_btn']))
        self.setIconSize(QSize(70,40))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 20pt 'Futura'; text-align: center;}")
        addr = self.text
        balance = str(self.bal) + ' PKT'
        msg_box_7 = QtWidgets.QMessageBox()
        msg_box_7.setText('Click show details below to see balance for address '+ addr )
        msg_box_7.setDetailedText("Balance: " + balance)
        msg_box_7.exec()
