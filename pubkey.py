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
    
def get_public_key(uname, pwd, progress_callback):
    global err
    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet validateaddress " + address
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        err = err.decode('utf-8')
        if err:
            print('Error:', err)
        else:
            result = json.loads(result)["pubkey"]
            return result

    except subprocess.CalledProcessError as e:
        print('Failed to retrieve public key.', e.output)

def get_key(u, p, a, win, state, pool):
    global window, uname, pwd, worker_state_active, address
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    address = a

    window.pk_line.setText('Retrieving key...')
    # Pass the function to execute
    if not worker_state_active['GET_PUB_KEY']:
        worker_state_active['GET_PUB_KEY'] = True
        worker = rpcworker.Worker(get_public_key, uname, pwd) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)

        # Execute
        threadpool.start(worker)

def print_result(result):
    window.pk_line.clear()
    if err:
        window.pk_line.setText(_translate("MainWindow","No address selected."))
    else:
        window.pk_line.setText(_translate("MainWindow",result))
    worker_state_active['GET_PUB_KEY'] = False
