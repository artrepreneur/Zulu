# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from rpcworker import progress_fn, thread_complete
from dropdowns import refresh_all
#from pixMp import *
from config import MIN_CONF, MAX_CONF

_translate = QCoreApplication.translate

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def get_all_addresses(uname, pwd, progress_callback):

    addr_d = {}
    temp_d = {}
    multisig_arr = []
    addr_arr = []

    try:
        
        if type == 'balances':
             addr_cmd_result = json.loads(subprocess.Popen([resource_path("bin/pktctl"), '-u', uname, '-P', pwd, '--wallet', 'getaddressbalances', MIN_CONF], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])
        else:
            addr_cmd_result = json.loads(subprocess.Popen([resource_path("bin/pktctl"), '-u', uname, '-P', pwd, '--wallet', 'getaddressbalances', MIN_CONF, 'True'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])


        for i, item in enumerate(addr_cmd_result):
            address = item["address"]
            confirmations = MIN_CONF

            balance = str(format(round(float(item["total"]), 8), '.8f'))
            confirmations += " or more confirmations"

            temp_d[address] = {'balance':balance, 'confirmations':confirmations}

        for i in sorted(temp_d.keys()):
            addr_d[i] = temp_d[i]

        temp_d2 = []
        temp_d3 = []

        for addr in addr_d:
            if addr[0] == "P":
                temp_d2.append(addr)
            else:
                temp_d3.append(addr)

        multisig_arr = temp_d2
        addr_arr = temp_d3

    except:
        print('Failed to retrieve addresses')

    return addr_arr, multisig_arr

def invoke_thread(uname, pwd, threadpool):
    worker = rpcworker.Worker(get_all_addresses, uname, pwd)
    worker.signals.result.connect(print_addresses)
    worker.signals.finished.connect(thread_complete)
    #worker.signals.progress.connect(progress_fn)
    threadpool.start(worker)

def get_addresses(u, p, win, t, state, pool):
    global window, uname, pwd, worker_state_active, type
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    type = t
    item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)


    # Pass the function to execute
    if type == "all" or type == "balances":
        if not worker_state_active['GET_ADDRESS']:
            worker_state_active['GET_ADDRESS']= True
            invoke_thread(uname, pwd, threadpool)
    elif type == "addresses":
        if not worker_state_active['GET_NEW_ADDRESS']:
            worker_state_active['GET_NEW_ADDRESS']= True
            invoke_thread(uname, pwd, threadpool)

    elif type == "multisig":
        if not worker_state_active['GET_MULTI_ADDR']:
            worker_state_active['GET_MULTI_ADDR']= True
            invoke_thread(uname, pwd, threadpool)

def print_addresses(addr):
    addr_dict = addr[0]
    multisig_arr = addr[1]
    list = []
    length = len(addr_dict)

    if length > 0:
        if type == 'balances' or type == 'all':
            window.balance_tree.clear()

        #icons = set_pixmaps()
        for addr in addr_dict:
            list.append(addr)

    else:
        msg = '*No addresses to add yet.'
        item_1 = QtWidgets.QTreeWidgetItem(window.balance_tree)
        window.balance_tree.topLevelItem(0).setText(0, _translate("MainWindow", msg))

    # refresh comboboxes in retrieve private key
    if not (type == 'balances'):
        refresh_all(window, list, 'addresses')
        refresh_all(window, multisig_arr, 'multisig')
        refresh_all(window, list + multisig_arr, 'all')

        # Reset flags
    if type == 'balances' or type == 'all':
        worker_state_active['GET_ADDRESS']= False
    elif type == 'addresses':
        worker_state_active['GET_NEW_ADDRESS']= False
    elif type == 'multisig':
        worker_state_active['GET_MULTI_ADDR']= False
