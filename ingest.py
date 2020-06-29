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
    
def ingest_keys(uname, pwd, progress_callback):
    global err, err_2

    try:
        cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if not err:
            try:
                for key in keys:
                    cmd_2 = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet importprivkey " + key.strip()
                    result_2, err_2 = (subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                    result_2 = result_2.decode('utf-8')
                    err_2 = err_2.decode('utf-8')
                    if err_2:
                        #window.import_text.clear()
                        #window.import_text.setPlaceholderText(_translate("MainWindow","Could not import, check key/s."))
                        break
                    else:
                        result_2 = 'success'

                return result_2
            except subprocess.CalledProcessError as e:
                print('Failed to retrieve key.', e.output)
        else:
            print('error:',err)

    except subprocess.CalledProcessError as e:
        print('Failed to unlock wallet, check password.', e.output)


def all_keys(u, p, k, pp, win, state, pool):
    global window, uname, pwd, worker_state_active, keys, passphrase
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    keys = k
    passphrase = pp

    window.import_text.clear()
    window.import_text.setPlainText('Importing ...')

    if not worker_state_active['IMP_PRIV_KEY']:
        worker_state_active['IMP_PRIV_KEY'] = True
        worker = rpcworker.Worker(ingest_keys, uname, pwd)
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)

        # Execute
        threadpool.start(worker)

def print_result(result):

    # Relock wallet.
    lock = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
    result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()
    window.import_text.clear()
    if result:
        window.import_text.setPlaceholderText(_translate("MainWindow","Keys successfully added."))
        i = window.stackedWidget.indexOf(window.added_keys_page)
        window.stackedWidget.setCurrentIndex(i)
    elif err:
        if 'ErrWrongPassphrase' in err:
            window.import_text.setPlaceholderText(_translate("MainWindow","Wrong wallet password entered."))
    else:
        window.import_text.setPlaceholderText(_translate("MainWindow","Could not import, check key/s."))
    worker_state_active['IMP_PRIV_KEY'] = False
