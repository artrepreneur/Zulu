# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
#from resource import resource_path
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def change_pass(uname, pwd, progress_callback):
    global err
    print('old_pwd', old_pwd)
    try:
        cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrasechange '" + old_pwd + "' '" + new_pwd + "'"
        result, err = subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        result = result.decode('utf-8')
        err = err.decode('utf-8')
        if err:
            print('Error:', err)
        return result

    except subprocess.CalledProcessError as e:
        print('Failed to retrieve public key.', e.output)

def change(u, p, op, np, win, state, pool):
    global window, uname, pwd, worker_state_active, old_pwd, new_pwd
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    old_pwd = op
    new_pwd = np
    window = win

    # Pass the function to execute
    if not worker_state_active['PASS_CHNG']:
        worker_state_active['PASS_CHNG'] = True
        worker = rpcworker.Worker(change_pass, uname, pwd) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)
        threadpool.start(worker)

def print_result(result):
    # Relock wallet.
    lock = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
    result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()

    if not err:
        msg_box_13 = QtWidgets.QMessageBox()
        msg_box_13.setText(_translate("MainWindow",'Your password has been changed.'))
        msg_box_13.exec()
    elif "Incorrect passphrase" in err:
        msg_box_13 = QtWidgets.QMessageBox()
        msg_box_13.setText(_translate("MainWindow",'Your password has not been changed. Please make sure your old password was entered correctly.'))
        msg_box_13.exec()
    else:
        msg_box_13 = QtWidgets.QMessageBox()
        msg_box_13.setText(_translate("MainWindow",'Your password has not been changed.'))
        msg_box_13.exec()    

    worker_state_active['PASS_CHNG'] = False
