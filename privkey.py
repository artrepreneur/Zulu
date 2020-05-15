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
    
def get_private_key(uname, pwd, progress_callback):
    global err, err_2

    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if not err:
            try:
                cmd_2 = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet dumpprivkey " + address
                result_2, err_2 = (subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                result_2 = result_2.decode('utf-8')
                err_2 = err_2.decode('utf-8')
                if err_2:
                    print('Error:', err_2)
                    return "Unable to retrieve private key."
                else:
                    return result_2

            except subprocess.CalledProcessError as e:
                print('Failed to retrieve key.', e.output)
        else:
            if "ErrWrongPassphrase" in err:
                print('Incorrect password.',err)
                window.lineEdit_9.clear()
                #window.lineEdit_9.setText("Incorrect password entered.")
    except subprocess.CalledProcessError as e:
        print('Failed to unlock wallet.', e.output)

def get_key(u, p, a, pp, win, state, pool):
    global window, uname, pwd, worker_state_active, address, passphrase
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    address = a
    passphrase = pp

    if address[0] == 'P':
        window.lineEdit_8.setText('Could not retrieve private key for multisig address.')
        return
    else:
        window.lineEdit_8.setText('Retrieving key...')
        # Pass the function to execute
        if not worker_state_active['GET_PRIV_KEY']:
            worker_state_active['GET_PRIV_KEY'] = True
            worker = rpcworker.Worker(get_private_key, uname, pwd) # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(print_result)
            worker.signals.finished.connect(thread_complete)
            worker.signals.progress.connect(progress_fn)

            # Execute
            threadpool.start(worker)

def print_result(result):
    # Relock wallet.
    lock = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
    result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()
    window.lineEdit_8.clear()
    if result:
        window.lineEdit_8.setText(_translate("MainWindow",result))
    else:
        window.lineEdit_8.setText(_translate("MainWindow","Could not retrieve, check wallet password."))
    worker_state_active['GET_PRIV_KEY'] = False
