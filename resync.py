import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def resync(uname, pwd, progress_callback):
    global err

    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet resync"
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')
        if err:
            print('Error:', err)
            return "Unable to retrieve private key."
        else:
            return result

    except subprocess.CalledProcessError as e:
        print('Failed to retrieve key.', e.output)

def execute(u, p, a, pp, win, state, pool):
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
        if not worker_state_active['RESYNC']:
            worker_state_active['RESYNC'] = True
            worker = rpcworker.Worker(resync, uname, pwd)
            worker.signals.result.connect(print_result)
            worker.signals.finished.connect(thread_complete)
            worker.signals.progress.connect(progress_fn)

            # Execute
            threadpool.start(worker)

def print_result(result):
        print("Resync in progress...")
        worker_state_active['RESYNC'] = False
