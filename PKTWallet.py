# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

from PyQt5 import QtWidgets, uic
from MainWindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
import os, sys, subprocess, json, threading, time, random, signal, traceback, re, psutil
import platform, transactions, estimate, ingest, signMultiSigTrans, sendMultiSigTrans, sendCombMultiSigTrans, fold, createWallet, getSeed, resync
import balances, addresses, balanceAddresses, rpcworker, privkey, pubkey, password, wlltinf, send, time, datetime, genMultiSig, createMultiSigTrans, sendCombMultiSigTrans
#import combineSigned
from pixMp import *
from genAddress import *
from config import MIN_CONF, MAX_CONF
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from shutil import copyfile
from pathlib import Path


VERSION_NUM = "1.0.0"
AUTO_RESTART_WALLET = False
CREATE_NEW_WALLET = False
SHUTDOWN_CYCLE = False
FEE = ".00000001"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Check if pkt wallet sync in progress
def pktwllt_synching():
    info = wlltinf.get_inf(uname, pwd)
    print('##', info)
    if info:
        try:
            return bool(info["WalletStats"]["Syncing"]).strip()
        except:
            print('Unable to get wallet status.')
            return False

# Check if pktd sync in progress
def pktd_synching():
    info = wlltinf.get_inf(uname, pwd)
    if info:
        try:
            return bool(info["IsSyncing"]).strip()
        except:
            print('Unable to get wallet status.')
            return False

# Message box for wallet sync
def sync_msg(msg):
    sync_msg_box = QtWidgets.QMessageBox()
    sync_msg_box.setText(msg)
    sync_msg_box.setWindowTitle('Sync Info')
    sync_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
    sync_ok_btn = sync_msg_box.button(QtWidgets.QMessageBox.Yes)
    sync_ok_btn.setText("Ok")
    sync_msg_box.exec()

# Add a new send recipient
class SendRcp(QtWidgets.QFrame):

    def __init__(self, obj_num, item, item_nm, *args, **kwargs):

        super(SendRcp, self).__init__(*args, **kwargs)
        self.obj_num = obj_num
        self.item = item
        self.name = item_nm

        self.setObjectName(self.name)
        self.setStyleSheet("background-color: rgb(228, 234, 235); margin-bottom: 0px; margin-right: 0px")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        self.verticalLayout_21 = QtWidgets.QFormLayout(self)
        self.verticalLayout_21.setObjectName("verticalLayout_21")

        self.label_9 = QtWidgets.QLabel(self)
        self.label_9.setStyleSheet("font: 16pt 'Helvetica'; padding-bottom: 4px;")
        self.label_9.setObjectName("label_9")
        self.label_9.setText("Pay To:")
        self.label_9.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.lineEdit_6 = QtWidgets.QLineEdit(self)
        self.lineEdit_6.setMinimumSize(QSize(0, 35))
        self.lineEdit_6.setMaximumSize(QSize(16777215, 35))
        self.lineEdit_6.setStyleSheet("background-color: rgb(253, 253, 255);")
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setToolTip("Enter Address of Payee")
        self.verticalLayout_21.addRow(self.label_9, self.lineEdit_6)
        self.verticalLayout_21.setFormAlignment(Qt.AlignLeft)
        self.verticalLayout_21.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.label_10 = QtWidgets.QLabel(self)
        self.label_10.setStyleSheet("font: 16pt 'Helvetica';padding-bottom: 4px;")
        self.label_10.setObjectName("label_10")
        self.label_10.setText("Amount:")
        self.send_amt_input = QtWidgets.QLineEdit(self)
        self.send_amt_input.setMinimumSize(QSize(0, 35))
        self.send_amt_input.setMaximumSize(QSize(16777215, 35))
        self.send_amt_input.setStyleSheet("background-color: rgb(253, 253, 255);")
        self.send_amt_input.setToolTip("Enter Amount to Pay")
        self.send_amt_input.setObjectName("send_amt_input")
        self.verticalLayout_21.addRow(self.label_10, self.send_amt_input)

        self.frme = QtWidgets.QFrame(self)
        self.frme.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frme.setMinimumHeight(5)
        self.frme.setMaximumHeight(5)

        self.del_rcp_1 = QtWidgets.QPushButton(self)
        self.del_rcp_1.setObjectName("pushButton")
        self.del_rcp_1.setText("Delete Recipient")
        self.del_rcp_1.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
        self.del_rcp_1.setMinimumHeight(40)
        self.verticalLayout_21.addRow(self.frme, self.del_rcp_1)
        self.del_rcp_1.clicked.connect(self.del_clicked)

    def del_fields(self):
        self.lineEdit_6.clear()
        self.send_amt_input.clear()

    def del_clicked(self):
        class_id = self.name.split('_')[0]
        chld_num = window.rcp_list.count() if (class_id == 'send') else window.rcp_list_2.count()

        if chld_num > 1 and class_id == 'send':
            window.rcp_list.removeItemWidget(self.item)
            window.rcp_list.takeItem(window.rcp_list.row(self.item))
            window.rcp_list.update()
            rcp_list_dict.pop(self.name)

            try:
                if pay_dict:
                    pay_dict.pop(self.lineEdit_6.text())
            except:
                print('unable to pop pay_dict', pay_dict)

        elif chld_num > 1 and class_id == 'multisig':
            window.rcp_list_2.removeItemWidget(self.item)
            window.rcp_list_2.takeItem(window.rcp_list_2.row(self.item))
            window.rcp_list_2.update()
            rcp_list_dict2.pop(self.name)

            try:
                if pay_dict2:
                    pay_dict2.pop(self.lineEdit_6.text())
            except:
                print('unable to pop pay_dict2', pay_dict2)


# Add a new public key entry field to multisig create
class PKLine(QtWidgets.QFrame):

    def __init__(self, obj_num, item, *args, **kwargs):

        super(PKLine, self).__init__(*args, **kwargs)
        self.item = item
        self.name = 'm_pkline_' + obj_num
        self.setObjectName(self.name)

        # New lineEdit
        self.pk_line = QtWidgets.QLineEdit(self)
        self.pk_line.setObjectName("pk_line_"+obj_num)
        self.pk_line.setStyleSheet("QLineEdit {background-color: rgb(253, 253, 255);}")
        self.pk_line.setMinimumHeight(40)

        # Del button
        self.del_btn = QtWidgets.QPushButton(self)
        self.del_btn.setObjectName("del_btn_"+obj_num)
        self.del_btn.setText("delete")
        self.del_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 16pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 16pt 'Futura'; background-color: #022D93; color: #FF6600;}")
        self.del_btn.setMinimumSize(60, 40)

        # Form layout
        self.form_layout = QtWidgets.QGridLayout(self)
        self.form_layout.addWidget(self.pk_line, 0, 0, 1, 1)
        self.form_layout.addWidget(self.del_btn, 0, 1, 1, 1)
        self.del_btn.clicked.connect(self.del_clicked)

    def del_clicked(self):
        chld_num = window.multisig_list.count()
        if chld_num > 1:
            if pk_list_dict:
                pk_list_dict.pop(self.name)
            window.multisig_list.removeItemWidget(self.item)
            window.multisig_list.takeItem(window.multisig_list.row(self.item))
            window.multisig_list.update()

class SideMenuBtn(QtWidgets.QPushButton):

    def __init__(self, obj_name, obj_text, icon_name, ttip, *args, **kwargs):
        super(SideMenuBtn, self).__init__(*args, **kwargs)
        self.text = obj_text
        self.name = obj_name
        self.icon_name = icon_name
        self.icon = icons[self.icon_name]
        self.ttip = ttip
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icon))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+"{border-radius: 3px; border: 1px solid #D6E4FF; color: #D6E4FF; font: 57 20pt 'Futura'; text-align: left;} QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))
        self.setToolTip(_translate("MainWindow", self.ttip))

    def mousePressEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.alt_name = self.icon_name + '2'
        self.icon2 = icons[self.alt_name]
        self.setIcon(QIcon(self.icon2))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 3px; border: 1px solid #FF6600; color: #FF6600; font: 57 20pt 'Futura'; background-color: #022D93;  text-align: left;}  QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))

    def mouseReleaseEvent(self, event):
        self.setText(self.text)
        self.setObjectName(self.name)
        self.setIcon(QIcon(self.icon))
        self.setIconSize(QSize(70,25))
        self.setStyleSheet("QPushButton#"+self.name+" {border-radius: 3px; border: 1px solid #D6E4FF; color: #D6E4FF; font: 57 20pt 'Futura';  text-align: left;}  QToolTip { color: #000; background-color: #fff; border: none; }")
        self.setMaximumSize(QSize(16777215,50))
        self.setMinimumSize(QSize(16777215,50))
        side_menu_clicked(self)

def side_menu_clicked(btn):

    #print('button pressed:', btn.objectName(), btn.objectName().split('_')[0])
    if btn.objectName().strip() == 'Balances':
        i = window.stackedWidget.indexOf(window.balance_page)
        #window.balance_tree.clear()
        #window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        show_balance()
        add_addresses(['balances'])

    elif btn.objectName().strip() == 'Send':
        window.label_6.clear()
        i = window.stackedWidget.indexOf(window.send_page)
        init_send_rcp()
        set_fee_est()

    elif btn.objectName().strip() == 'Receive':
        i = window.stackedWidget.indexOf(window.receive_page)
        window.receive_amt_line.clear()
        window.receive_hist_tree2.clear()
        window.msg_line.clear()
        window.label_26.clear()

    elif btn.objectName().strip() == 'Transaction':
        global iteration

        i = window.stackedWidget.indexOf(window.transactions_page)
        iteration = 0
        item_0 = QtWidgets.QTreeWidgetItem(window.transaction_hist_tree)
        font = QFont()
        font.setFamily("Helvetica")
        font.setPointSize(15)
        item_0.setFont(0, font)
        if pktd_synching():
            sync_msg("Transactions aren\'t available until wallet has completely sync\'d")
            #window.transaction_hist_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Wallet Syncing..."))
        else:
            window.transaction_hist_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        get_transactions()

    window.stackedWidget.setCurrentIndex(i)

def get_transactions():
    global iteration

    try:
        transactions.history(uname, pwd, iteration, window, worker_state_active, threadpool)
        iteration += 1
    except:
        msg = "Unable to get transactions. \n\nHave any transactions been executed?"
        trns_msg_box = QtWidgets.QMessageBox()
        trns_msg_box.setWindowTitle("Transaction History Failed")
        trns_msg_box.setText(msg)
        trns_msg_box.exec()
        print('Unable to get transactioss')

def show_balance():
    if pktd_synching(): 
        sync_msg("Wallet daemon is currently syncing. Some features may not work until sync is complete.")
    elif pktwllt_synching():
        sync_msg('Wallet is currently synching to chain. Some balances may be inaccurate until chain sync\'s fully.')

    window.balance_amount.clear()
    worker_state_active['GET_BALANCE'] = False
    total_balance = balances.get_balance_thd(uname, pwd, window, worker_state_active, threadpool)
    #total_balance = balances.get_balance(uname, pwd)
    #window.balance_amount.setText(_translate("MainWindow", total_balance))
    #worker_state_active['GET_BALANCE'] = True

def set_fee_est():
    global FEE
    estimate.fee(uname, pwd, window, FEE, worker_state_active, threadpool)

# Append addresses to list
def add_addresses(type):

    for item in type:
        if item == "balances" or item == "all":
            # Add loading message
            load_label= QtWidgets.QLabel()
            load_label.setStyleSheet("font: 16pt \'Helvetica\'; padding-bottom: 4px; text-align: center;")
            load_label.setText("Addresses loading please wait...")
            load_label.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            balanceAddresses.get_addresses(uname, pwd, window, item, worker_state_active, threadpool)

        elif item == "addresses":
            addresses.get_addresses(uname, pwd, window, item, worker_state_active, threadpool)

def get_priv_key(address, passphrase):
    # Get private key
    privkey.get_key(uname, pwd, address, passphrase, window, worker_state_active, threadpool)

def get_pub_key(address):
    # Get private key
    pubkey.get_key(uname, pwd, address, window, worker_state_active, threadpool)

def change_pass(old_pass, new_pass):
    # Attempt to change password.
    password.change(uname, pwd, old_pass, new_pass, window, worker_state_active, threadpool)

# Additional customizations
def add_custom_styles():

    window.label_25.setPixmap(QPixmap(resource_path('img/app_icon.png')))

    # Frame customizations
    window.send_exec_group.setStyleSheet("QGroupBox#send_exec_group {border-radius: 5px; background-color: rgb(228, 234, 235);}")
    window.send_exec_group.setMinimumHeight(73)
    window.send_exec_group.setMaximumHeight(73)

    # Button cusomizations
    window.clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.clear_btn.setMinimumSize(50, 40)

    window.fold_btn_1.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fold_btn_1.setMinimumSize(80, 40)

    window.snd_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.snd_btn.setMinimumSize(50, 40)

    window.add_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_btn.setMinimumSize(50, 40)

    window.multi_clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_clear_btn.setMinimumSize(50, 40)

    window.fee_est2_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fee_est2_btn.setMinimumSize(100, 40)

    window.fee_est_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.fee_est_btn.setMinimumSize(100, 40)

    window.import_keys_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.import_keys_btn.setMinimumSize(80, 40)

    window.multi_add_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_add_btn.setMinimumSize(50, 40)

    window.multi_create_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_create_btn.setMinimumSize(50, 40)

    window.multi_sign_btn2.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn2.setMinimumSize(50, 40)

    window.multi_sign_btn3.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn3.setMinimumSize(50, 40)

    window.multi_sign_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_sign_btn.setMinimumSize(160, 40)

    window.import_trans_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.import_trans_btn.setMinimumSize(160, 40)

    window.multi_send_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_send_btn.setMinimumSize(160, 40)

    window.combine_trans_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.combine_trans_btn.setMinimumSize(180, 40)

    window.add_trns_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_trns_btn.setMinimumSize(180, 40)

    window.comb_clear_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.comb_clear_btn.setMinimumSize(180, 40)

    window.combine_send_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.combine_send_btn.setMinimumSize(180, 40)

    window.rtr_pubk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.rtr_pubk_btn.setFixedSize(180, 40)

    window.rtr_prvk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.rtr_prvk_btn.setFixedSize(180, 40)

    window.file_loc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.file_loc_btn.setFixedSize(100, 40)

    window.multi_create_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_create_btn.setMinimumSize(100, 40)

    window.address_gen_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.address_gen_btn.setFixedSize(100, 40)

    window.multi_qr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multi_qr_btn.setFixedSize(100, 40)

    window.address_gen_btn2.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.address_gen_btn2.setMinimumHeight(40)

    window.all_addr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.all_addr_btn.setMinimumHeight(40)

    window.bal_addr_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.bal_addr_btn.setMinimumHeight(40)

    window.receive_rqst_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.receive_rqst_btn.setFixedSize(200, 40)

    window.multisig_gen_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.multisig_gen_btn.setFixedSize(100, 40)

    window.add_multisig_pk_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.add_multisig_pk_btn.setFixedSize(140, 40)

    window.pwd_ok_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.pwd_ok_btn.setMinimumSize(50, 40)

    window.pwd_cancel_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.pwd_cancel_btn.setMinimumSize(50, 40)

    window.sign_dec_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.sign_dec_btn.setMinimumSize(50, 40)

    window.sign_enc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.sign_enc_btn.setMinimumSize(50, 40)

    window.load_trns_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.load_trns_btn.setFixedSize(100, 40)

    window.wllt_cr8_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.wllt_cr8_btn.setFixedSize(120, 40)

    window.passphrase_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.passphrase_btn.setFixedSize(120, 40)

    window.seed_next_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.seed_next_btn.setMinimumSize(150, 40)

    window.no_seed_next_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.no_seed_next_btn.setMinimumSize(150, 40)

    window.open_wllt_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.open_wllt_btn.setFixedSize(100, 40)

    window.recalc_btn.setStyleSheet("QPushButton {border-radius: 5px; border: 1px solid rgb(2, 45, 147); font: 57 14pt 'Futura';} QPushButton:pressed {border-radius: 5px; border: 1px solid #FF6600; font: 57 14pt 'Futura'; background-color: #022D93; color: #FF6600;}")
    window.recalc_btn.setFixedSize(100, 25)

# Listen for static buttons
def button_listeners():
    window.snd_btn.clicked.connect(btn_released)
    window.clear_btn.clicked.connect(btn_released)
    window.multi_clear_btn.clicked.connect(btn_released)
    window.fee_est2_btn.clicked.connect(btn_released)
    window.fee_est_btn.clicked.connect(btn_released)
    window.add_btn.clicked.connect(btn_released)
    window.add_multisig_pk_btn.clicked.connect(btn_released)
    window.multi_add_btn.clicked.connect(btn_released)
    window.address_gen_btn.clicked.connect(btn_released)
    window.address_gen_btn2.clicked.connect(btn_released)
    window.all_addr_btn.clicked.connect(btn_released)
    window.bal_addr_btn.clicked.connect(btn_released)
    window.multi_create_btn.clicked.connect(btn_released)
    window.multi_sign_btn2.clicked.connect(btn_released)
    window.multi_sign_btn3.clicked.connect(btn_released)
    window.import_trans_btn.clicked.connect(btn_released)
    window.combine_trans_btn.clicked.connect(btn_released)
    window.combine_send_btn.clicked.connect(btn_released)
    window.multi_sign_btn.clicked.connect(btn_released)
    window.add_trns_btn.clicked.connect(btn_released)
    window.comb_clear_btn.clicked.connect(btn_released)
    window.fold_btn_1.clicked.connect(btn_released)
    window.multi_send_btn.clicked.connect(btn_released)
    window.rtr_prvk_btn.clicked.connect(btn_released)
    window.rtr_pubk_btn.clicked.connect(btn_released)
    window.pwd_cancel_btn.clicked.connect(btn_released)
    window.pwd_ok_btn.clicked.connect(btn_released)
    window.load_trns_btn.clicked.connect(btn_released)
    window.import_keys_btn.clicked.connect(btn_released)
    window.receive_rqst_btn.clicked.connect(btn_released)
    window.multisig_gen_btn.clicked.connect(btn_released)
    window.multi_qr_btn.clicked.connect(btn_released)
    window.wllt_cr8_btn.clicked.connect(btn_released)
    window.passphrase_btn.clicked.connect(btn_released)
    window.seed_next_btn.clicked.connect(btn_released)
    window.no_seed_next_btn.clicked.connect(btn_released)
    window.open_wllt_btn.clicked.connect(btn_released)
    window.recalc_btn.clicked.connect(btn_released)


# Menu listeners
def menubar_listeners():
    window.actionAddress_2.triggered.connect(menubar_released)
    window.actionMultiSig_Address.triggered.connect(menubar_released)
    window.actionCreate_Transaction.triggered.connect(menubar_released)
    window.actionPassword.triggered.connect(menubar_released)
    window.actionPay_to_Many.triggered.connect(menubar_released)
    window.actionSign_Verify_Message.triggered.connect(menubar_released)
    window.actionCombine_Multisig_Transactions.triggered.connect(menubar_released)
    window.actionExport_Private_Key.triggered.connect(menubar_released)
    window.actionImport_Keys.triggered.connect(menubar_released)
    window.actionDelete.triggered.connect(menubar_released)
    window.actionInformation_2.triggered.connect(menubar_released)
    window.actionGet_Public_Key.triggered.connect(menubar_released)
    window.actionEncrypt_Decrypt_Message.triggered.connect(menubar_released)
    window.actionSave.triggered.connect(menubar_released)
    window.actionGet_Private_Key.triggered.connect(menubar_released)
    window.actionSeed.triggered.connect(menubar_released)
    window.actionFrom_Text_2.triggered.connect(menubar_released)
    window.actionFrom_QR_Code.triggered.connect(menubar_released)
    window.actionFold_Address.triggered.connect(menubar_released)
    window.actionWebsite.triggered.connect(menubar_released)
    window.actionManual_Resync.triggered.connect(menubar_released)
    app.aboutToQuit.connect(quit_app)

# Quit app
def quit_app():
    global SHUTDOWN_CYCLE
    SHUTDOWN_CYCLE = True
    exit_handler()


# Handler for menu item click
def btn_released(self):
    global FEE

    clicked_widget = window.sender()
    #print('pressed button:', clicked_widget.objectName())

    if clicked_widget.objectName() == 'add_multisig_pk_btn':
        #print('add new pk line here')
        if window.multisig_list.count() < 12:
            item_num = window.multisig_list.count() + 1
            item_line_N = QtWidgets.QListWidgetItem(window.multisig_list)
            item_line_N.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
            window.multisig_list.addItem(item_line_N)
            item_nm = "m_pkline_"+ str(item_num)
            vars()[item_nm] = PKLine(str(item_num), item_line_N)
            window.multisig_list.setItemWidget(item_line_N, vars()[item_nm])
            pk_list_dict[item_nm] = vars()[item_nm]

    elif clicked_widget.objectName() == 'multisig_gen_btn':
        global pk_arr, pk_count
        pk_arr = []
        for val in list(pk_list_dict.values()):
            itm = val.pk_line.text().strip()
            if itm:
                pk_arr.append(itm)

        pk_count = int(window.sig_box.currentText())
        msg_box_16 = QtWidgets.QMessageBox()

        if len(pk_arr) >= pk_count:
            print("Correct number of public keys entered.")

            for i, item in enumerate(pk_arr):
                if not item:
                    msg = "All public keys must be valid. Delete any extra input fields you don't need."
                    msg_box_16.setText(msg)
                    msg_box_16.exec()
                    return

            #Get passphrase
            passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

            if ok:
                msg = "Create new multisig address?"
                msg_box_16.setText(msg)
                msg_box_16.exec()
                genMultiSig.create(uname, pwd, window, pk_count, pk_arr, passphrase, worker_state_active, threadpool)
        else:
            msg = "Incorrect number of public keys."
            msg_box_16.setText(msg)
            msg_box_16.exec()
            print("Incorrect number of public keys.")

    elif clicked_widget.objectName() == 'add_trns_btn':
        import_qr2()

    elif clicked_widget.objectName() == 'comb_clear_btn':
        clear_comb()

    elif clicked_widget.objectName() == 'clear_btn':
        clear_send_rcp()

    elif clicked_widget.objectName() == 'multi_clear_btn':
        clear_multi_rcp()

    elif clicked_widget.objectName() == 'fee_est_btn':
        set_fee_est()

    elif clicked_widget.objectName() == 'fee_est2_btn':
        set_fee_est()

    elif clicked_widget.objectName() == 'wllt_cr8_btn':
        window.lineEdit_2.clear()
        window.lineEdit_11.clear()
        i = window.stackedWidget.indexOf(window.wllt_pwd_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_widget.objectName() == 'passphrase_btn':
        global wllt_pass
        wllt_pass = window.lineEdit_2.text().strip()
        wllt_pass_conf = window.lineEdit_11.text().strip()

        if not (wllt_pass or wllt_pass_conf):
            wllt_pass = ''
            wll_pass_conf = ''
            msg_box_24 = QtWidgets.QMessageBox()
            msg_box_24.setText('You must enter both a password and a confirmation.')
            msg_box_24.exec()
            return

        if wllt_pass == wllt_pass_conf:
            msg = ''
            if len(wllt_pass) < 8:
                msg = "Make sure your password is at least 8 letters"
            elif re.search('[0-9]',wllt_pass) is None:
                msg = "Make sure your password has a number in it"
            elif re.search('[A-Z]',wllt_pass) is None:
                msg = "Make sure your password has a capital letter in it"
            if msg:
                msg_box_24 = QtWidgets.QMessageBox()
                msg_box_24.setText(msg)
                msg_box_24.exec()
                return

            window.imprt_seed_txt.clear()
            window.old_pass_line.clear()
            i = window.stackedWidget.indexOf(window.imprt_seed_page)
            window.stackedWidget.setCurrentIndex(i)
            imp_msg_box = QtWidgets.QMessageBox()
            text = "Select \"Continue Without Seed\" if you are not importing a previous wallet seed."
            imp_msg_box.setText(text)
            imp_msg_box.setWindowTitle("Notification")
            ret = imp_msg_box.exec()

        else:
            wllt_pass = ''
            wll_pass_conf = ''
            msg_box_24 = QtWidgets.QMessageBox()
            msg_box_24.setText('Password and password confirmation do not match.')
            msg_box_24.exec()

    elif clicked_widget.objectName() == 'no_seed_next_btn':
        try:
            pp = wllt_pass
            window.seed_txt.clear()
            seed = createWallet.execute(uname,pwd, pp)["seed"]
            window.seed_txt.setText(seed)
            i = window.stackedWidget.indexOf(window.wllt_done_page)
            window.stackedWidget.setCurrentIndex(i)
        except:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
            seed_msg_box.exec()

    elif clicked_widget.objectName() == 'seed_next_btn':
        pp = wllt_pass
        seed_entry = window.imprt_seed_txt.toPlainText().strip() #.split()
        #print('seed entry:', seed_entry)
        old_pass_line = window.old_pass_line.text().strip()

        if not old_pass_line:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('You failed to enter your old password.')
            seed_msg_box.exec()
            return
        if len(seed_entry.split()) == 15:
            try:
                seed = createWallet.seed_execute(uname, pwd, pp, old_pass_line, seed_entry)["seed"]
                if not seed:
                    seed_msg_box = QtWidgets.QMessageBox()
                    seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
                    seed_msg_box.exec()
                else:
                    window.seed_txt.setText(seed)
                    i = window.stackedWidget.indexOf(window.wllt_done_page)
                    window.stackedWidget.setCurrentIndex(i)
            except:
                seed_msg_box = QtWidgets.QMessageBox()
                seed_msg_box.setText('Your wallet could not be created. Verify seed and/or old password.')
                seed_msg_box.exec()
        else:
            seed_msg_box = QtWidgets.QMessageBox()
            seed_msg_box.setText('Your seed has an incorrect number of words. Check your seed and try again.')
            seed_msg_box.exec()

    elif clicked_widget.objectName() == 'recalc_btn':
        show_balance()

    elif clicked_widget.objectName() == 'open_wllt_btn':
        start_wallet_thread()
        window.menubar.setEnabled(True)
        #window.resize(1000, 800)
        window.menu_frame.show()
        window.balance_tree.clear()
        i = window.stackedWidget.indexOf(window.balance_page)
        window.stackedWidget.setCurrentIndex(i)
        show_balance()
        add_addresses(['balances'])
        add_addresses(['addresses'])

    elif clicked_widget.objectName() == 'fold_btn_1':
        window.label_77.clear()
        fr = window.fld_frm_box.currentText()
        to = window.fld_to_box.currentText()
       
        # Handle empty addresses
        if fr == '':
            # Select a fold address.
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('You must select an address to fold from.')
            msg_box_26.exec()
            return 

        elif to == '':
            # If you have no fold addresses, click here to generate one.
            msg_box_26= QtWidgets.QMessageBox()
            msg_box_26.setText('You must select an address to fold to. Do you wish to create a new fold address?')
            msg_box_26.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            msg_box_26.setDefaultButton(QtWidgets.QMessageBox.Yes)
            snd_yes_btn = msg_box_26.button(QtWidgets.QMessageBox.Yes)
            snd_no_btn = msg_box_26.button(QtWidgets.QMessageBox.No)
            msg_box_26.exec()
            if msg_box_26.clickedButton() == snd_yes_btn:
                window.address_gen_btn2.click()
            return

        passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

        if ok:
            #Get passphrase
            fold.execute(uname, pwd, window, worker_state_active, threadpool, passphrase, fr, to)

        else:
            msg_box_18= QtWidgets.QMessageBox()
            msg_box_18.setText('You must enter your wallet passphase to submit transaction')
            msg_box_18.exec()

    elif clicked_widget.objectName() == 'add_btn':
        global rcp_list_dict, pay_dict

        if rcp_list_dict:
            last_key = list(rcp_list_dict.keys())[-1]
            last_item_num = last_key.split('_')[-1]
            item_num = int(last_item_num) + 1

        else:
            item_num = window.rcp_list.count() + 1

        item_line_N = QtWidgets.QListWidgetItem(window.rcp_list)
        item_line_N.setSizeHint(QSize((window.rcp_list.width() - 30), window.rcp_list.height()))
        window.rcp_list.addItem(item_line_N)
        item_nm = "send_rcp_"+ str(item_num)
        vars()[item_nm] = SendRcp(str(item_num), item_line_N, item_nm)
        window.rcp_list.setItemWidget(item_line_N, vars()[item_nm])
        rcp_list_dict[item_nm] = vars()[item_nm]
        window.rcp_list.setCurrentRow(int(window.rcp_list.count()))
        window.rcp_list.repaint() #.update()

    elif clicked_widget.objectName() == 'multi_add_btn':
        global rcp_list_dict2, pay_dict2

        if rcp_list_dict2:
            last_key = list(rcp_list_dict2.keys())[-1]
            last_item_num = last_key.split('_')[-1]
            item_num = int(last_item_num) + 1

        else:
            item_num = window.rcp_list_2.count() + 1

        item_num = window.rcp_list_2.count() + 1
        item_line_N = QtWidgets.QListWidgetItem(window.rcp_list_2)
        item_line_N.setSizeHint(QSize((window.rcp_list_2.width() - 30), window.rcp_list_2.height()))
        window.rcp_list_2.addItem(item_line_N)
        item_nm = "multisig_rcp_"+ str(item_num)
        vars()[item_nm] = SendRcp(str(item_num), item_line_N, item_nm)
        window.rcp_list_2.setItemWidget(item_line_N, vars()[item_nm])
        window.rcp_list_2.repaint()
        rcp_list_dict2[item_nm] = vars()[item_nm]

        #for i in rcp_list_dict2:
        #    print('payto:', rcp_list_dict2[i].lineEdit_6.text().strip())
        #    print('amt:', rcp_list_dict2[i].send_amt_input.text().strip())

    elif clicked_widget.objectName() == 'multi_qr_btn':

        # pop up with QR pk_arr
        pks = '| '.join(pk_arr)
        qr_text = 'qr_type: MULTI_QR, public_keys: '+ pks +' , m: '+str(pk_count)

        # Write QR
        qr_c = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )

        qr_c.add_data(qr_text)
        qr_c.make(fit=True)

        img = qr_c.make_image(fill_color="black", back_color="white")

        fn = "addmultiqr.png"
        img.save(resource_path("QRCodes/"+fn))

        # Show QR
        msg_box_25 = QtWidgets.QMessageBox()
        msg_box_25.setIconPixmap(QPixmap(resource_path("QRCodes/"+fn)))
        msg_box_25.setInformativeText('Scan QR code here.')
        msg_box_25.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
        ret = msg_box_25.exec()

        # Save QR elsewhere for convenient sharing.
        if ret == QtWidgets.QMessageBox.Save:
            dir = QDir.homePath()
            dlg = QtWidgets.QFileDialog()
            dlg.setDefaultSuffix(".padding")
            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]
            if filename:
                img.save(resource_path(filename))

        elif ret == QtWidgets.QMessageBox.Cancel:
            return

    elif clicked_widget.objectName() == 'receive_rqst_btn':
        pay_to_addr = str(window.pay_to_combo_box.currentText())
        amt = window.receive_amt_line.text()

        try:
            amt = float(amt)
        except:
            window.receive_amt_line.clear()
            window.receive_amt_line.setPlaceholderText('Input must be a number value.')
            return

        amt = str(amt)
        pay_msg = window.msg_line.text()

        dt= str(datetime.datetime.now()).split('.')[0]

        if pay_to_addr[0] == 'P':
            qr_text = 'qr_type: MULTI_PAY_REQUEST, date: '+ dt +',pay_to: ' + pay_to_addr +',amount: ' + amt + ',comment: ' + pay_msg
        else:
            qr_text = 'qr_type: PAY_REQUEST, date: '+ dt +',pay_to: ' + pay_to_addr +',amount: ' + amt + ',comment: ' + pay_msg

        # Write QR
        qr_c = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_c.add_data(qr_text)
        qr_c.make(fit=True)

        img = qr_c.make_image(fill_color="black", back_color="white")

        #img = qrcode.make(qr_text)
        fn = "requests.png"
        img.save(resource_path("QRCodes/"+fn))

        # Show QR
        msg_box_15 = QtWidgets.QMessageBox()
        msg_box_15.setIconPixmap(QPixmap(resource_path("QRCodes/"+fn)))
        msg_box_15.setInformativeText('Scan QR code here.')
        msg_box_15.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
        ret = msg_box_15.exec()

        # Save QR elsewhere for convenient sharing.
        if ret == QtWidgets.QMessageBox.Save:
            dir = QDir.homePath()
            dlg = QtWidgets.QFileDialog()
            dlg.setDefaultSuffix(".padding")
            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]
            if filename:
                img.save(resource_path(filename))

        elif ret == QtWidgets.QMessageBox.Cancel:
            return

        window.label_26.setText(_translate("MainWindow","Share the QR code you saved with the party you are requesting payment from."))
        window.label_26.setStyleSheet("font: 16pt 'Helvetica'")

    elif clicked_widget.objectName() == 'address_gen_btn':
        if not pktwllt_synching() == "True":
            get_new_address(uname, pwd, window, worker_state_active, threadpool)
        else:
            msg = 'Wallet is syncing, this will not work until sync is complete.'
            sync_msg(msg)

    elif clicked_widget.objectName() == 'pwd_cancel_btn':
        window.lineEdit_4.clear()
        window.lineEdit_5.clear()
        window.lineEdit_10.clear()

    elif clicked_widget.objectName() == 'pwd_ok_btn':
        old_pass = window.lineEdit_10.text().strip()
        new_pass = window.lineEdit_4.text().strip()
        new_pass_cfm = window.lineEdit_5.text().strip()

        if old_pass.isalnum() and new_pass.isalnum() and new_pass_cfm.isalnum():

            if new_pass_cfm != new_pass:
                msg_box_12 = QtWidgets.QMessageBox()
                msg_box_12.setText('Make sure your new password matches your password confirmation.')
                msg_box_12.exec()
            else:
                if worker_state_active['PASS_CHNG'] == False:
                    change_pass(old_pass, new_pass)
                    print('attempt to change old_pass password')
        else:
            msg_box_12 = QtWidgets.QMessageBox()
            msg_box_12.setText('Make sure your passwords are alphanumeric.')
            msg_box_12.exec()

    elif clicked_widget.objectName() == 'address_gen_btn2':
        window.address_line.clear()
        window.pubkey_line.clear()
        i = window.stackedWidget.indexOf(window.address_create_page)
        window.stackedWidget.setCurrentIndex(i)
        inf_msg_box = QtWidgets.QMessageBox()
        inf_msg_box.setText('Just click generate to create an address.')
        inf_msg_box.exec()

    elif clicked_widget.objectName() == 'all_addr_btn' and not worker_state_active['GET_ADDRESS']:
        window.balance_tree.clear()
        item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)
        window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        i = window.stackedWidget.indexOf(window.balance_page)
        window.stackedWidget.setCurrentIndex(i)
        add_addresses(['all'])

    elif clicked_widget.objectName() == 'bal_addr_btn' and not worker_state_active['GET_ADDRESS']:
        window.balance_tree.clear()
        item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)
        window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", "Loading..."))
        add_addresses(['balances'])

    elif clicked_widget.objectName() == 'multi_create_btn':
        global multisig_trans
        window.label_65.clear()
        pay_dict2 = {}
        address = str(window.comboBox_2.currentText())
        FEE = window.lineEdit_3.text()
        is_valid = True
        for i in rcp_list_dict2:
            pay_to = rcp_list_dict2[i].lineEdit_6.text().strip()
            amt = rcp_list_dict2[i].send_amt_input.text().strip()
            amt_isnum = False

            if pay_to == address:
                msg_box_17 = QtWidgets.QMessageBox()
                msg_box_17.setText('Cannot submit transaction. Payee and payer must be different.')
                msg_box_17.exec()
                is_valid = False
                return

            try:
                amt = float(amt)
                amt_isnum = True

            except:
                amt_isnum = False

            if amt_isnum and pay_to.isalnum():
                pay_dict2[pay_to] = amt

            else:
                msg_box_17 = QtWidgets.QMessageBox()
                msg_box_17.setText('Cannot submit transaction. Make sure all payees have a valid address and amount.')
                msg_box_17.exec()
                is_valid = False
                return

        if len(rcp_list_dict2) > 0:

            #Get passphrase
            passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

            if ok:
                result = createMultiSigTrans.create(uname, pwd, amt, address, pay_dict2, FEE, passphrase, window)
                err_result = str(result).split(':')[0]
                if err_result == "Error":
                    msg_box_18 = QtWidgets.QMessageBox()
                    msg_box_18.setText(result)
                    msg_box_18.exec()
                else:
                    #QR gen
                    global multisig_trans
                    multisig_trans = str(result)
                    trans_len = len(bytes.fromhex(result.strip()))

                    if trans_len <= 1276:
                        qr_text = 'qr_type: MULTISIG_TRANS, transactions:' + multisig_trans.strip('\n')
                        qr_c = qrcode.QRCode(
                            version=25,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr_c.add_data(qr_text)
                        qr_c.make(fit=True)

                        img = qr_c.make_image(fill_color="black", back_color="white")
                        #img = qrcode.make(qr_text)
                        fn = "multitrans.png"
                        img.save(resource_path("QRCodes/"+fn))
                        msg_box = QtWidgets.QMessageBox()
                        msg_box.setText('Scan QR code here, or use "Show Details" to copy transaction.')
                        qr = QPixmap(resource_path("QRCodes/"+fn))
                        msg_box.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                        msg_box.setDetailedText(str(result))
                        msg_box.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                        ret = msg_box.exec()

                        if ret == QtWidgets.QMessageBox.Save:
                            try:
                                dir = QDir.homePath()
                                dlg = QtWidgets.QFileDialog()
                                dlg.setDefaultSuffix(".padding")
                                filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn,"", " (.png)"))[0]

                                if filename:
                                    img.save(resource_path(filename))
                            except:
                                return

                        elif ret == QtWidgets.QMessageBox.Cancel:
                            return
                    else:
                        i = window.stackedWidget.indexOf(window.raw_multi_trans_page)
                        window.stackedWidget.setCurrentIndex(i)
                        window.raw_mult_trans.clear()
                        window.raw_mult_trans.setText(multisig_trans)

            else:
                msg_box_18= QtWidgets.QMessageBox()
                msg_box_18.setText('You must enter your wallet passphase to submit transaction')
                msg_box_18.exec()

    elif clicked_widget.objectName() == 'import_trans_btn':
        import_qr()

    elif clicked_widget.objectName() == 'multi_sign_btn':
        raw_trans = (str(window.trans_text.toPlainText())).strip()
        passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

        if ok:
            result = signMultiSigTrans.create(uname, pwd, raw_trans, passphrase, window)
            err_result = str(result).split(':')[0]

            if err_result == "Error":
                msg_box_19 = QtWidgets.QMessageBox()
                msg_box_19.setText(result)
                msg_box_19.exec()
            else:
                window.signed_text.setText(result)
                signed_multisig_trans = str(result)
                qr_text = 'qr_type: SIGNED_MULTISIG_TRANS, transactions: ' + signed_multisig_trans
                #print('qr_text', qr_text)
                try:
                    trans_len = len(bytes.fromhex(signed_multisig_trans))
                    if trans_len <= 1276:
                        qr_c = qrcode.QRCode(
                            version=25,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr_c.add_data(qr_text)
                        qr_c.make(fit=True)

                        img = qr_c.make_image(fill_color="black", back_color="white")

                        #img = qrcode.make(qr_text)
                        fn = "signed-multitrans.png"
                        img.save(resource_path("QRCodes/"+fn))
                        msg_box_20 = QtWidgets.QMessageBox()
                        msg_box_20.setText('Scan QR code here, or use "Show Details" to copy transaction.')
                        qr = QPixmap(resource_path("QRCodes/"+fn))
                        msg_box_20.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                        msg_box_20.setDetailedText(str(result))
                        msg_box_20.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                        ret = msg_box_20.exec()

                        if ret == QtWidgets.QMessageBox.Save:
                            dir = QDir.homePath()
                            dlg = QtWidgets.QFileDialog()
                            dlg.setDefaultSuffix(".padding")
                            filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]

                            if filename:
                                img.save(resource_path(filename))

                        elif ret == QtWidgets.QMessageBox.Cancel:
                            return
                except:
                    return

        else:
            msg_box_19 = QtWidgets.QMessageBox()
            msg_box_19.setText('You must enter your wallet passphase to submit transaction')
            msg_box_19.exec()

    elif (clicked_widget.objectName() == 'multi_sign_btn2') or (clicked_widget.objectName() == 'multi_sign_btn3'):
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.stackedWidget.setCurrentIndex(i)

        try:
            window.trans_text.clear()
            window.signed_text.clear()
            window.signed_text.repaint()
            window.label_66.clear()
            window.trans_text.setText(multisig_trans)
            window.trans_text.repaint()
            window.trans_text.setPlaceholderText("Use import button to import multisig transactions here, or copy and paste them in.")
            msg_box_2 = QtWidgets.QMessageBox()
            msg_box_2.setText('Your multisig transaction has been auto-populated here. Just click sign to sign the transaction.')
            msg_box_2.exec()
        except:
            window.trans_text.setPlaceholderText("Could not auto-populate multisig transaction. You must create a transaction first. If a transaction was created, use import button to load it.")#Use import transaction from menu or paste raw transaction here.

    elif clicked_widget.objectName() == 'multi_send_btn':

        #required_sigs = True
        msg_box_3 = QtWidgets.QMessageBox()
        msg_box_3.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        snd_yes_btn = msg_box_3.button(QtWidgets.QMessageBox.Yes)
        snd_no_btn = msg_box_3.button(QtWidgets.QMessageBox.No)
        raw_trans = (str(window.signed_text.toPlainText())).strip()
        result = sendMultiSigTrans.create(uname, pwd, FEE, raw_trans, window)
        err_result = str(result["result"]).split(':')[0]

        if err_result == "Error":
            msg_box_19 = QtWidgets.QMessageBox()
            msg_box_19.setText(result["result"])
            msg_box_19.exec()

        elif err_result == "Cancel":
            return

        else:
            i = window.stackedWidget.indexOf(window.sent_page)
            window.stackedWidget.setCurrentIndex(i)
            window.lineEdit_7.setText(result["result"])
            window.textEdit_4.setText(result["details"])

    elif clicked_widget.objectName() == 'snd_btn':
        global pay_dict

        #Get passphrase
        passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

        if ok:

            pay_dict = {}
            address = str(window.pay_from_combo_box.currentText())
            msg_box_3d = QtWidgets.QMessageBox()
            is_valid = True
            for i in rcp_list_dict:
                pay_to = rcp_list_dict[i].lineEdit_6.text().strip()
                amt = rcp_list_dict[i].send_amt_input.text().strip()


                if pay_to == address:
                    msg_box_3d.setText('Cannot submit transaction. Payee and payer must be different.')
                    msg_box_3d.exec()
                    is_valid = False
                    return


                amt_isnum = False
                try:
                    amt = float(amt)
                    amt_isnum = True
                except:
                    amt_isnum = True

                if amt_isnum and pay_to.isalnum():
                    pay_dict[pay_to] = amt
                    #print('payto:', pay_to)
                    #print('amt:', amt)

                else:
                    msg_box_3d.setText('Cannot submit transaction. Make sure all payees have a valid address and amount.')
                    msg_box_3d.exec()
                    is_valid = False
                    return #break

            if is_valid:
                msg_box_3b = QtWidgets.QMessageBox()
                msg_box_3b.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                msg_box_3b.setDefaultButton(QtWidgets.QMessageBox.Yes)
                snd_yes_btn = msg_box_3b.button(QtWidgets.QMessageBox.Yes)
                snd_no_btn = msg_box_3b.button(QtWidgets.QMessageBox.No)
                msg_box_3b.setText('Are you sure you \nwish to send?')
                msg_box_3b.exec()

                if msg_box_3b.clickedButton() == snd_yes_btn:

                    send.execute2(uname, pwd, address, passphrase, pay_dict, window, worker_state_active)
                    
        else:
            msg_box_3a = QtWidgets.QMessageBox()
            msg_box_3a.setText('You must enter your wallet passphase to submit transaction')
            msg_box_3a.exec()

    elif clicked_widget.objectName() == 'import_keys_btn':
        txt = window.import_text.toPlainText()
        keys = txt.replace('\n',' ').split()
        passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter wallet passphrase:',QtWidgets.QLineEdit.Password)

        if ok:
            ingest.all_keys(uname, pwd, keys, passphrase, window, worker_state_active, threadpool)

    elif clicked_widget.objectName() == 'send_comb_btn':
        msg_box_3b = QtWidgets.QMessageBox()
        msg_box_3b.setText('You do not have the required number of signatures to submit this transaction.')
        msg_box_3b.exec()

    elif clicked_widget.objectName() == 'rtr_prvk_btn':
        address = str(window.comboBox_5.currentText())
        passphrase = str(window.lineEdit_9.text().strip())
        if address[0] == 'P':
            msg_box_10 = QtWidgets.QMessageBox()
            msg_box_10.setText("Can't retrieve private key for multisig address.")
            msg_box_10.exec()
            return

        if address.isalnum() and passphrase.isalnum():
            get_priv_key(address, passphrase)
        else:
            msg_box_10 = QtWidgets.QMessageBox()
            msg_box_10.setText('Make sure to select and address and enter your wallet passphrase to retrieve your private key.')
            msg_box_10.exec()

    elif clicked_widget.objectName() == 'rtr_pubk_btn':
        address = str(window.addr_combo.currentText())
        if address[0] == 'P':
            msg_box_11 = QtWidgets.QMessageBox()
            msg_box_11.setText("Can't retrieve public key for multisig address.")
            msg_box_11.exec()
            return
        if address.isalnum():
            get_pub_key(address)
        else:
            msg_box_11 = QtWidgets.QMessageBox()
            msg_box_11.setText('Make sure to select and address  to retrieve your public key.')
            msg_box_11.exec()

    elif clicked_widget.objectName() == 'combine_trans_btn':
        signed_trans_list = window.add_trans_txt.toPlainText()
        signed_trans_arr = signed_trans_list.split('\n')
        signed_trans_arr = [item for item in signed_trans_arr if item!='']
        result = "Unable to combine transactions."#combineSigned.combine(uname, pwd, window, signed_trans_arr)
        multi_comb_trans = str(result)
        window.combine_trans_txt.setText(multi_comb_trans)
        window.combine_trans_txt.repaint()

        try:
            trans_len = len(bytes.fromhex(result))
            qr_text = 'qr_type: COMBINED_MULTISIG_TRANS, transactions: ' + multi_comb_trans
            if trans_len <= 1276:
                qr_c = qrcode.QRCode(
                    version=25,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_c.add_data(qr_text)
                qr_c.make(fit=True)

                img = qr_c.make_image(fill_color="black", back_color="white")
                #img = qrcode.make(qr_text)

                fn = "combined-multitrans.png"
                img.save(resource_path("QRCodes/"+fn))
                msg_box_22 = QtWidgets.QMessageBox()
                msg_box_22.setText('Scan QR code here, or use "Show Details" to copy the combined multisig transaction.')
                qr = QPixmap(resource_path("QRCodes/"+fn))
                msg_box_22.setIconPixmap(qr.scaled(QSize(400,400), Qt.KeepAspectRatio))
                msg_box_22.setDetailedText(str(multi_comb_trans))
                msg_box_22.setStandardButtons(QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel)
                ret = msg_box_22.exec()

                try:
                    if ret == QtWidgets.QMessageBox.Save:
                        dir = QDir.homePath()
                        dlg = QtWidgets.QFileDialog()
                        dlg.setDefaultSuffix(".padding")
                        filename = (dlg.getSaveFileName(None, "Save QR", dir + "/" + fn, "*.png"))[0]

                        if filename:
                            img.save(resource_path(filename))

                    elif ret == QtWidgets.QMessageBox.Cancel:
                        return

                except:
                    print("QR operation failed")
        except:
            return

    elif clicked_widget.objectName() == 'combine_send_btn':
        window.label_69.clear()
        try:
            multi_comb_trans = window.combine_trans_txt.toPlainText()
            result = sendCombMultiSigTrans.create(uname, pwd, FEE, multi_comb_trans, window)
            err_result = str(result["result"]).split(':')[0]

            if err_result == "Error":
                msg_box_22 = QtWidgets.QMessageBox()
                msg_box_22.setText(result["result"])
                msg_box_22.exec()

            elif err_result == "Cancel":
                return

            else:
                i = window.stackedWidget.indexOf(window.sent_page)
                window.stackedWidget.setCurrentIndex(i)
                window.lineEdit_7.setText(result["result"])
                window.textEdit_4.setText(result["details"])
        except:
            msg_box_22 = QtWidgets.QMessageBox()
            msg_box_22.setText("Transaction send failed. Check that all necessary signatures have been combined.")
            msg_box_22.exec()
            window.label_69.setText("Transaction send failed. Check that all necessary signatures have been combined.")

    elif clicked_widget.objectName() == 'load_trns_btn':
        get_transactions()

def menubar_released(self):
    global FEE
    clicked_item = window.sender().objectName()
    #print('pressed menubar item', clicked_item)
    if clicked_item == 'actionAddress_2':
        window.address_line.clear()
        window.pubkey_line.clear()
        i = window.stackedWidget.indexOf(window.address_create_page)
        window.stackedWidget.setCurrentIndex(i)
        inf_msg_box = QtWidgets.QMessageBox()
        inf_msg_box.setText('Just click generate to create an address.')
        inf_msg_box.exec()

    elif clicked_item == 'actionMultiSig_Address':
        i = window.stackedWidget.indexOf(window.multisig_create_page)
        init_multisig()
        window.stackedWidget.setCurrentIndex(i)
        msg_box_8 = QtWidgets.QMessageBox()
        msg_box_8.setText('Select "Add Public Key" to add more signatures to your multisig address.')
        msg_box_8.exec()

    elif clicked_item == 'actionCreate_Transaction':
        init_multi_rcp()
        set_fee_est()
        window.label_55.setText("Generate a raw multisig transaction here.")
        window.label_65.clear()
        i = window.stackedWidget.indexOf(window.multisig_send_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionPassword':
        window.lineEdit_10.clear()
        window.lineEdit_4.clear()
        window.lineEdit_5.clear()
        i = window.stackedWidget.indexOf(window.password_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionSave':
        wallet_file = str(wallet_db)
        save_dir = QDir.homePath()
        name = "wallet.db"
        dlg = QtWidgets.QFileDialog()
        dlg.setDefaultSuffix(".db")
        filename = str(dlg.getSaveFileName(None, "save file", save_dir + "/" + name,"", "DB (.db)")[0])

        try:
            copyfile(wallet_file, filename)
        except:
            print('Wallet file could not be copied.')


    elif clicked_item == 'actionDelete':
        wallet_file = wallet_db

        if wallet_file != '':
            msg_box_5 = QtWidgets.QMessageBox()
            text = 'Are you sure you wish to delete this wallet?\n'# + wallet_file
            msg_box_5.setText(text)
            msg_box_5.setWindowTitle("Delete Wallet")
            del_yes = QtWidgets.QMessageBox.Yes
            del_no = QtWidgets.QMessageBox.No
            msg_box_5.setStandardButtons(del_yes | del_no)
            msg_box_5.setDefaultButton(del_yes)
            ret = msg_box_5.exec()
            del_msg_box = QtWidgets.QMessageBox()
            del_msg_box.setWindowTitle("Wallet Delete Status")
            success = False

            if (ret == QtWidgets.QMessageBox.Yes):
                print("Deleting wallet.")
                success = True
                try:
                    os.remove(wallet_file)
                    msg = "Wallet Deleted. \n\nDo you wish to set up a new wallet?"
                    cont_yes = QtWidgets.QMessageBox.Yes
                    cont_no = QtWidgets.QMessageBox.No
                    del_msg_box.setStandardButtons(cont_yes | cont_no)
                    del_msg_box.setDefaultButton(cont_yes)
                except:
                    msg = "Wallet not deleted."
                    print(msg)

            elif (ret == QtWidgets.QMessageBox.No):
                msg = "Wallet not deleted."
                print(msg)

            del_msg_box.setText(msg)
            cont = del_msg_box.exec()

            if cont == QtWidgets.QMessageBox.Yes and success:
                # Kill wallet, then restart it
                global AUTO_RESTART_WALLET
                if os_sys == 'Linux' or os_sys == 'Darwin':
                    try:
                        subprocess.call(['pkill', 'signal', 'SIGINT', 'wallet'], shell=False)
                        AUTO_RESTART_WALLET = True
                    except:
                        sys.exit()

                elif os_sys == 'Windows':
                    try:
                        os.system("taskkill /f /im  wallet.exe")
                        AUTO_RESTART_WALLET = True
                    except:
                        sys.exit()

                window.menu_frame.hide()
                window.menubar.setEnabled(False)
                i = window.stackedWidget.indexOf(window.new_wallet_page)
                window.stackedWidget.setCurrentIndex(i)

            elif cont == QtWidgets.QMessageBox.No and success:
                exit_handler()
                sys.exit()

    elif clicked_item == 'actionPay_to_Many':
        window.label_6.clear()
        i = window.stackedWidget.indexOf(window.send_page)
        window.stackedWidget.setCurrentIndex(i)
        msg_box_1 = QtWidgets.QMessageBox()
        msg_box_1.setText('Select "Add Recipients" below to pay to multiple addresses.')
        msg_box_1.exec()

    elif clicked_item == 'actionFrom_Text_2':
        window.trans_text.clear()
        window.signed_text.clear()
        window.label_66.clear()
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionFrom_QR_Code':
        import_qr()

    elif clicked_item == 'actionFold_Address':
        window.label_77.clear()
        i = window.stackedWidget.indexOf(window.fold_page_1)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionWebsite':
        url = QUrl('https://github.com/artrepreneur/PKT-Cash-Wallet')
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')
    
    elif clicked_item == 'actionManual_Resync':
        sync_msg("Wallet Resync Starting. This could take a while.")
        resync.execute(uname, pwd, window, worker_state_active, threadpool)

    elif clicked_item == 'actionSeed':
        passphrase, ok = QtWidgets.QInputDialog.getText(window, 'Wallet Passphrase', 'Enter your wallet passphrase to access your seed:',QtWidgets.QLineEdit.Password)

        if ok:
            try:
                window.seed_txt_2.clear()
                seed = getSeed.execute(uname, pwd, passphrase, window, worker_state_active) #, threadpool
                if seed:
                    window.seed_txt_2.setText(seed)
                    i = window.stackedWidget.indexOf(window.get_seed_page)
                    window.stackedWidget.setCurrentIndex(i)

            except:
                print('Wrong wallet passphrase entered.')
                msg_box_13 = QtWidgets.QMessageBox()
                msg_box_13.setText('Wrong wallet passphrase entered.')
                msg_box_13.exec()


    elif clicked_item == 'actionSign_Verify_Message' or clicked_item == 'actionCreate_Transaction':
        i = window.stackedWidget.indexOf(window.load_sign_verify_page)
        window.trans_text.clear()
        window.signed_text.clear()
        window.label_66.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionCombine_Multisig_Transactions':
        i = window.stackedWidget.indexOf(window.combine_multi_page)
        window.add_trans_txt.clear()
        window.combine_trans_txt.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionExport_Private_Key':
        i = window.stackedWidget.indexOf(window.export_keys_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionImport_Keys':
        i = window.stackedWidget.indexOf(window.import_page)
        window.import_text.clear()
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionInformation_2':

        info = wlltinf.get_inf(uname, pwd)
        if info:
            try:
                window.ver.setText(VERSION_NUM)
                window.blks.setText(str(info["CurrentHeight"]))
                window.dsync.setText(str(info["IsSyncing"]))
                window.isync.setText(str(info["WalletStats"]["Syncing"]))
                window.bstp.setText(str(info["CurrentBlockTimestamp"]))
                window.bhsh.setText(str(info["CurrentBlockHash"]))
            except:
                print('Unable to get wallet info')
        else:
            msg_box_14 = QtWidgets.QMessageBox()
            msg_box_14.setText('Your wallet information could not be retrieved. Please wait for wallet to sync and retry.')
            msg_box_14.exec()

        i = window.stackedWidget.indexOf(window.information_page)
        window.stackedWidget.setCurrentIndex(i)

    elif clicked_item == 'actionGet_Public_Key':
        i = window.stackedWidget.indexOf(window.pubkey_page)
        window.pk_line.clear()
        window.stackedWidget.setCurrentIndex(i)
        #window.addr_combo.addItems(['Loading addresses ...'])

    elif clicked_item == 'actionGet_Private_Key':
        i = window.stackedWidget.indexOf(window.privkey_page)
        window.lineEdit_9.clear()
        window.lineEdit_8.clear()
        window.stackedWidget.setCurrentIndex(i)
        #window.comboBox_5.addItems(['Loading addresses ...'])

    elif clicked_item == 'actionEncrypt_Decrypt_Message':
        i = window.stackedWidget.indexOf(window.enc_msg_page)
        window.textEdit_2.clear()
        window.textEdit_3.clear()
        window.stackedWidget.setCurrentIndex(i)

def import_qr2():
    dir = QDir.homePath()
    dlg2 = QtWidgets.QFileDialog()
    filename = dlg2.getOpenFileName(None, _translate("MainWindow","Open QR"), dir + "/", "*.png")

    try:
        qr_dict = {}
        qr_data = str((decode(Image.open(filename[0]))[0].data).decode('utf-8')).split(',')

        for i, item in enumerate(qr_data):
            item_list = item.split(':')
            key = item_list[0].strip()
            val = item_list[1].strip()
            qr_dict[key] = val

        if qr_dict['qr_type'] == 'SIGNED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.add_trans_txt.append(transactions+'\n\n')
        elif qr_dict['qr_type'] == 'COMBINED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.combine_trans_txt.setText(transactions)

    except:
        print("Unable to retrieve QR File")
        window.add_trans_txt.setPlaceholderText("QR not a valid signed multisig transaction.")

    return

def import_qr():
    dir = QDir.homePath()
    dlg2 = QtWidgets.QFileDialog()
    filename = dlg2.getOpenFileName(None, _translate("MainWindow","Open QR"), dir + "/", "*.png")
    try:
        qr_dict = {}
        qr_data = str((decode(Image.open(filename[0]))[0].data).decode('utf-8')).split(',')
        for i, item in enumerate(qr_data):
            item_list = item.split(':')
            key = item_list[0].strip()
            val = item_list[1].strip()
            qr_dict[key] = val

        if qr_dict['qr_type'] == 'PAY_REQUEST':
            window.label_6.clear()
            i = window.stackedWidget.indexOf(window.send_page)
            window.stackedWidget.setCurrentIndex(i)
            init_send_rcp()
            pay_to = list(rcp_list_dict.values())[0].lineEdit_6.setText(qr_dict['pay_to'])
            amt = list(rcp_list_dict.values())[0].send_amt_input.setText(qr_dict['amount'])

        elif qr_dict['qr_type'] == 'MULTI_PAY_REQUEST':
            window.label_65.clear()
            i = window.stackedWidget.indexOf(window.multisig_send_page)
            window.stackedWidget.setCurrentIndex(i)
            init_multi_rcp()
            pay_to = list(rcp_list_dict2.values())[0].lineEdit_6.setText(qr_dict['pay_to'])
            amt = list(rcp_list_dict2.values())[0].send_amt_input.setText(qr_dict['amount'])

        elif qr_dict['qr_type'] == 'MULTISIG_TRANS':
            window.trans_text.clear()
            window.signed_text.clear()
            window.label_66.clear()
            i = window.stackedWidget.indexOf(window.load_sign_verify_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.trans_text.setText(transactions)

        elif qr_dict['qr_type'] == 'SIGNED_MULTISIG_TRANS':
            window.trans_text.clear()
            window.signed_text.clear()
            window.label_66.clear()
            i = window.stackedWidget.indexOf(window.load_sign_verify_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.signed_text.setText(transactions)

        elif qr_dict['qr_type'] == 'COMBINED_MULTISIG_TRANS':
            window.combine_trans_txt.clear()
            i = window.stackedWidget.indexOf(window.combine_multi_page)
            window.stackedWidget.setCurrentIndex(i)
            transactions = qr_dict['transactions']
            window.combine_trans_txt.setText(transactions)

        elif qr_dict['qr_type'] == 'MULTI_QR':
            public_keys = qr_dict['public_keys'].split('|')
            m = qr_dict['m']
            window.multisig_list.clear()

            for i in range(len(public_keys)):
                item_line_x = QtWidgets.QListWidgetItem(window.multisig_list)
                item_line_x.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
                window.multisig_list.addItem(item_line_x)
                item_nm = "m_pkline_"+ str(i+1)
                vars()[item_nm] = PKLine(str(i+1), item_line_x)
                window.multisig_list.setItemWidget(item_line_x, vars()[item_nm])
                pk_list_dict[item_nm] = vars()[item_nm]
                (pk_list_dict[item_nm]).pk_line.setText(public_keys[i])
            window.sig_box.setCurrentText(str(m))
            i = window.stackedWidget.indexOf(window.multisig_create_page)
            window.stackedWidget.setCurrentIndex(i)

    except:
        print("Unable to retrieve QR File")

    return


# Check if procs are running     
def chk_live_proc():
    
    proc_array = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['name']=='wallet':
            proc_array.append('wallet')
        if proc.info['name']=='pktd':
            proc_array.append('pktd') 
    return proc_array

def kill_procs(procs):
    global os_sys
    os_sys = platform.system()
    if len(procs) > 0:
        if not SHUTDOWN_CYCLE: # At start up
            msg_box_X = QtWidgets.QMessageBox()
            proc_text = ('a ' + procs[0]) if len(procs) == 1 else ('a ' + procs[0] + ' and a '+ procs[1]) 
            text = 'You are running ' + proc_text + ' instance. Would you like to kill all instances?'
            msg_box_X.setText(text)
            msg_box_X.setWindowTitle("Kill Daemon")
            kill_yes = QtWidgets.QMessageBox.Yes
            kill_no = QtWidgets.QMessageBox.No
            msg_box_X.setStandardButtons(kill_yes | kill_no)
            msg_box_X.setDefaultButton(kill_yes)
            ret = msg_box_X.exec()

            if (ret == QtWidgets.QMessageBox.Yes):
                print('Restarting daemons...')
                kill_it()
            else:
               print('Quitting application...')
               sys.exit()

        else: # At shutdown
            kill_it()
            sys.exit()

def kill_it():
    global AUTO_RESTART_WALLET
    try:
        AUTO_RESTART_WALLET = False
        print(os_sys)
        if os_sys == 'Linux' or os_sys == 'Darwin':
            subprocess.call(['pkill', 'signal','SIGINT', 'wallet'], shell=False)
            time.sleep(10)
            subprocess.call(['pkill', 'signal', 'SIGINT', 'pktd'], shell=False)
        elif os_sys == 'Windows':
            os.system("taskkill /f /im  wallet.exe")
            time.sleep(10)
            os.system("taskkill /f /im  pktd.exe")
        time.sleep(10)        
    except:
        print('Failed to clean up.')    


# Cleanup on exit
def exit_handler():
    print("Cleaning up...")       
    procs = chk_live_proc()
    if procs:
        kill_procs(procs)

def restart(proc):
    print('process:', proc)
    rst_msg_box = QtWidgets.QMessageBox()
    if proc == "pktwallet":
        process = "PKT wallet"
    else:
        process = "PKT daemon"
    msg = process + ' has died, would you like to restart it?'
    rst_msg_box.setText(msg)
    rst_msg_box.setWindowTitle('Process Restart')
    rst_msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
    rst_ok_btn = rst_msg_box.button(QtWidgets.QMessageBox.Yes)
    rst_ok_btn.setText("Ok")
    ret = rst_msg_box.exec()

    if ret == QtWidgets.QMessageBox.Yes:
        try:
            if proc == "pktwallet":
                start_wallet_thread()
            else:
                start_pktd_thread()
        except:
            print("Process could not be restarted.")
            sys.exit()

    elif ret == QtWidgets.QMessageBox.Cancel:
        sys.exit()


# Thread PKT wallet
def start_wallet_thread():
    pktwallet_cmd_result = inv_pktwllt()
    worker = Worker(pktwllt_worker, pktwallet_cmd_result)
    worker.signals.result.connect(pktwllt_dead)
    threadpool.start(worker)

def pktwllt_dead():
    print('$$Wallet died', SHUTDOWN_CYCLE)
    if not SHUTDOWN_CYCLE:
        if not AUTO_RESTART_WALLET and wallet_db != '':
            restart('pktwallet')
        else:
            start_wallet_thread()
    
# Thread PKT Daemon
def start_pktd_thread():
    pktd_cmd_result = inv_pktd()
    worker = Worker(pktd_worker, pktd_cmd_result)
    worker.signals.result.connect(pktd_dead)
    threadpool.start(worker)

def pktd_dead():
    print('$$pktd died', SHUTDOWN_CYCLE)
    if not SHUTDOWN_CYCLE:
        restart('pktd')

def inv_pktd():
    global pktd_pid, pktd_cmd_result
    print('Invoking PKTD ...')
    pktd_cmd = "bin/pktd -u "+uname+" -P " +pwd+ " --txindex --addrindex"
    pktd_cmd_result = subprocess.Popen(resource_path(pktd_cmd), shell=True, stdout=subprocess.PIPE)
    pktd_pid = pktd_cmd_result.pid + 1
    return pktd_cmd_result

def pktd_worker(pktd_cmd_result, progress_callback):
    print('Running PKTD Worker ...')
    while pktd_cmd_result.poll() is None or int(pktd_cmd_result.poll()) > 0:
        print(str((pktd_cmd_result.stdout.readline()).decode('utf-8')))
    return

def inv_pktwllt():
    print('Invoking PKT Wallet ...')
    global pktwallet_pid, pktwallet_cmd_result
    pktwallet_cmd_result = subprocess.Popen([resource_path('bin/wallet'), '-u', uname, '-P', pwd], shell=False, stdout=subprocess.PIPE)
    pktwallet_pid = pktwallet_cmd_result.pid + 1
    pktwllt_stdout = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
    status = ''

    # Loop until wallet successfully opens.
    while not ('Opened wallet' in status) and (pktwallet_cmd_result.poll() is None):
        pktwllt_stdout = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
        print('pktwllt_stdout:',pktwllt_stdout)
        if pktwllt_stdout:
            status = pktwllt_stdout
    return pktwallet_cmd_result

def pktwllt_worker(pktwallet_cmd_result, progress_callback):
    print('Running PKT Wallet Worker ...')

    # Watch the wallet to ensure it stays open.
    while True:
        output = str((pktwallet_cmd_result.stdout.readline()).decode('utf-8'))
        print(output)
        if not pktwallet_cmd_result.poll() is None or output =='': 
            break    
    return

def start_daemon(uname, pwd):
    global pktd_pid, pktwallet_pid
    pktd_pid = 0
    pktwallet_pid = 0

    if wallet_db != '':
        try:
            start_pktd_thread()
            start_wallet_thread()
        except:
            print('Failed to invoke daemon.')
            exit_handler()
            sys.exit()
    else:
        try:
            global CREATE_NEW_WALLET
            print('Creating a new wallet...')
            CREATE_NEW_WALLET = True
            start_pktd_thread()
            window.menu_frame.hide()
            window.menubar.setEnabled(False)
            i = window.stackedWidget.indexOf(window.new_wallet_page)
            window.stackedWidget.setCurrentIndex(i)

        except:
            print('Failed to invoke pktd daemon.')
            exit_handler()
            sys.exit()


def get_wallet_db():
    wallet_db = ''
    get_db_cmd = "bin/getwalletdb"
    get_db_result = (subprocess.Popen(resource_path(get_db_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
    print('get_db_result:', get_db_result) 
    if get_db_result.strip() != "Path not found":    
        wallet_db = get_db_result.strip('\n')+'/wallet.db'
        print('Wallet location:', wallet_db)
    else:
        wallet_db = ''
    print('wallet_db', wallet_db)        
    return wallet_db    

def clear_send_rcp():
    global rcp_list_dict, pay_dict

    keys = list(rcp_list_dict.keys())
    for key in keys:
        rcp_list_dict[key].del_clicked()

    # still clear last remaining fields here.
    if (rcp_list_dict):
        item = list(rcp_list_dict.values())[0]
        item.del_fields()

        # Clear out dict's
        pay_dict = {}

def clear_comb():
    window.add_trans_txt.clear()
    window.add_trans_txt.repaint()
    window.combine_trans_txt.clear()
    window.combine_trans_txt.repaint()
    window.add_trans_txt.setPlaceholderText("Use import button to import signed transactions here, or copy and paste them in.")
    i = window.stackedWidget.indexOf(window.combine_multi_page)
    window.stackedWidget.setCurrentIndex(i)

def clear_multi_rcp():
    global rcp_list_dict2, pay_dict2

    keys = list(rcp_list_dict2.keys())
    for key in keys:
        rcp_list_dict2[key].del_clicked()

    # still clear last remaining fields here.
    if (rcp_list_dict2):
        item = list(rcp_list_dict2.values())[0]
        item.del_fields()

        # Clear out dict's
        pay_dict = {}


def init_send_rcp():
    global rcp_list_dict, pay_dict
    window.rcp_list.clear()
    rcp_list_dict = {} # reset
    pay_dict = {}
    window.rcp_list.setAutoScrollMargin(5)
    window.rcp_list.setStyleSheet("margin: 0px")
    item_line_y = QtWidgets.QListWidgetItem(window.rcp_list)
    item_line_y.setSizeHint(QSize((window.rcp_list.width() - 30), window.rcp_list.height()))
    window.rcp_list.addItem(item_line_y)
    item_nm = "send_rcp_"+ str(1)
    vars()[item_nm] = SendRcp(str(1), item_line_y, item_nm)
    window.rcp_list.setItemWidget(item_line_y, vars()[item_nm])
    rcp_list_dict[item_nm] = vars()[item_nm]

def init_multi_rcp():
    global rcp_list_dict2, pay_dict2
    rcp_list_dict2 = {}
    pay_dict2 = {}
    window.rcp_list_2.clear()
    window.rcp_list_2.setAutoScrollMargin(5)
    item_line_z = QtWidgets.QListWidgetItem(window.rcp_list_2)
    item_line_z.setSizeHint(QSize((window.rcp_list_2.width() - 30), window.rcp_list_2.height()))
    window.rcp_list_2.addItem(item_line_z)
    item_nm = "multisig_rcp_"+ str(1)
    vars()[item_nm] = SendRcp(str(1), item_line_z, item_nm)
    window.rcp_list_2.setItemWidget(item_line_z, vars()[item_nm])
    rcp_list_dict2[item_nm] = vars()[item_nm]

def init_multisig():
    global pk_list_dict
    pk_list_dict = {}
    window.label_13.clear()
    window.label_13.setText("To create a multi signature address, enter the public keys of all the participants. Maximum of 12 allowed.")
    window.multisig_list.clear()
    for i in range(3):
        item_line_x = QtWidgets.QListWidgetItem(window.multisig_list)
        item_line_x.setSizeHint(QSize(window.multisig_list.width() - 30, 60))
        window.multisig_list.addItem(item_line_x)
        item_nm = "m_pkline_"+ str(i+1)
        vars()[item_nm] = PKLine(str(i+1), item_line_x)
        window.multisig_list.setItemWidget(item_line_x, vars()[item_nm])
        pk_list_dict[item_nm] = vars()[item_nm]

'''
def init_multi_cmb():

    #window.add_trans_list.setAutoScrollMargin(5)
    item_line_w = QtWidgets.QListWidgetItem(window.add_trans_list)
    item_line_w.setSizeHint(QSize((window.add_trans_list.width() - 90), window.add_trans_list.height()))
    window.add_trans_list.addItem(item_line_w)
    item_nm = "trans_item_1"
    vars()[item_nm] = TransLine("1", item_line_w)
    window.add_trans_list.setItemWidget(item_line_w, vars()[item_nm])
'''
def init_side_menu():
    balance_btn = SideMenuBtn('Balances', 'Balances', 'pixmap_balance_btn', 'View Your Balances')
    send_btn = SideMenuBtn('Send', 'Send', 'pixmap_send_btn', 'Send PKT Cash')
    receive_btn = SideMenuBtn('Receive', 'Receive', 'pixmap_receive_btn', 'Receive PKT Cash')
    transaction_btn = SideMenuBtn('Transaction', 'Transaction', 'pixmap_transaction_btn', 'View Transaction History')
    grid = QtWidgets.QGridLayout(window.frame_3)
    grid.addWidget(balance_btn, 0, 0)
    grid.addWidget(send_btn, 1, 0)
    grid.addWidget(receive_btn, 2, 0)
    grid.addWidget(transaction_btn, 3, 0)
    grid.setSpacing(0)
    grid.setContentsMargins(0,0,0,0)
    window.frame_3.setLayout(grid)

def deactivate():
    window.receive_groupBox_2.hide()
    window.comboBox_3.hide()
    window.label_41.hide()
    window.multi_add_btn.hide()
    window.add_btn.hide()
    window.actionPay_to_Many.setVisible(False)
    window.actionEncrypt_Decrypt_Message.setVisible(False)
    window.actionCombine_Multisig_Transactions.setVisible(False)

    # Fee related buttons
    window.fee_est2_btn.hide()
    window.fee_est_btn.hide()
    window.frame_2.hide()
    window.lineEdit_6.hide()

def init_size():
    window.setMinimumSize(1100, 580)
    window.stackedWidget.setCurrentIndex(0)
    window.balance_tree.header().setMinimumHeight(40)
    window.transaction_hist_tree.header().setMinimumHeight(40)
    window.receive_hist_tree2.header().setMinimumHeight(40)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

# ----- MAIN -----
if __name__ == "__main__":

    _translate = QCoreApplication.translate
    iteration = 0
    wallet_db = get_wallet_db()
    
    worker_state_active = {
        'GET_ADDRESS':False,
        'GET_BALANCE': False,
        'GET_NEW_ADDRESS': False,
        'GET_PRIV_KEY': False,
        'GET_PUB_KEY': False,
        'PASS_CHNG': False,
        'TRANS': False,
        'EST': False,
        'SEND_PAY': False,
        'IMP_PRIV_KEY': False,
        'GET_MULTI_ADDR': False,
        'FOLD_WALLET': False,
        'GET_SEED': False,
        'RESYNC': False
    }

    # Randomized Auth
    uname = str(random.getrandbits(128))
    pwd = str(random.getrandbits(128))

    # Set up app
    app = QtWidgets.QApplication(sys.argv)
    icons = set_pixmaps()
    window = MainWindow()
    window.raise_() #added for pyinstaller only, else menubar fails

    # Shutdown any other instances
    exit_handler()

    # Size the app
    init_size()

    # Add multisig pubkeys lines
    init_multisig()

    # Add initial send recipient form - normal transaction
    init_send_rcp()

    # Add initial send recipient form - multisig transaction
    init_multi_rcp()

    # Add side menu buttons
    init_side_menu()

    # Temporarily deactivated for later version, or future deprecation
    deactivate()

    # Set up threadpool
    threadpool = QThreadPool()

    # Fire up daemon and wallet backend
    print('Starting Daemon ...')
    start_daemon(uname, pwd)

    # show balance
    #print('create new wallet', CREATE_NEW_WALLET)
    
    if not CREATE_NEW_WALLET:
        # Add balances
        print('Getting Balance ...')
        show_balance()

        # Add address balances and addresses
        print('Getting Address Balances ...')
        add_addresses(['balances'])
        add_addresses(['addresses'])

    # Styling
    add_custom_styles()

    # Listeners
    button_listeners()
    menubar_listeners()
    window.show()
    
    app.exec()
