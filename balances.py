# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess
import os, sys, rpcworker
from PyQt5.QtCore import *
from config import MIN_CONF, MAX_CONF
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def get_balance(uname, pwd, progress_callback):
    bal_cmd_result, err = (subprocess.Popen([resource_path('bin/pktctl'), '-u', uname, '-P', pwd, '--wallet', 'getbalance'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    bal_cmd_result = bal_cmd_result.decode('utf-8')
    print('bal_cmd_result', bal_cmd_result)
    err = err.decode('utf-8')
    print(bal_cmd_result, err)

    if not err:
        bal_cmd_result = round(float(bal_cmd_result),8)
        return str(bal_cmd_result).rstrip()

def get_balance_for_addr(uname, pwd, addr):
    addr_bal_cmd_result, err = (subprocess.Popen([resource_path('bin/pktctl'), '-u', uname, '-P', pwd, '--wallet', 'listunspent', MIN_CONF, MAX_CONF, '[\"'+addr+'\"]'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    addr_bal_cmd_result = addr_bal_cmd_result.decode('utf-8')
    err = err.decode('utf-8')

    if not err:
        bal = 0
        for itm in addr_bal_cmd_result:
            tmp_bal = round(float(itm["amount"]),4)
            bal += tmp_bal
        return str(bal)

def get_balance_thd(u, p, win, state, pool):
    global window, uname, pwd, worker_state_active
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool

    # Pass the function to execute
    if not worker_state_active['GET_BALANCE']:
        window.balance_amount.setText(_translate("MainWindow", "Calculating..."))
        worker_state_active['GET_BALANCE'] = True
        worker = rpcworker.Worker(get_balance, uname, pwd)
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        #worker.signals.progress.connect(progress_fn)

        # Execute
        threadpool.start(worker)        

def print_result(result):
    window.balance_amount.clear()
    if result:
        window.balance_amount.setText(_translate("MainWindow", result))
    else:
        window.balance_amount.setText(_translate("MainWindow", "Failed to retrieve balance."))
    worker_state_active['GET_BALANCE'] = False