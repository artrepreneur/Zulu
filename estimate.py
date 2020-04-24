import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
#from resource import resource_path
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate

BLOCKS = 10

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

    
def get_est(uname, pwd, progress_callback):
    global err
    err = False
    

    # estimatefee RPC isn't implemented yet
    '''
    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet estimatefee " + str(BLOCKS)
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if err:
            print('Error:', err)
            return .00000001
        else:
            print('Fee estimate:', result)
            return result

    except subprocess.CalledProcessError as e:
        print('Failed to retrieve fee estimate.', e.output)
        return .00000001
    '''
    return .0000001

def fee(u, p, win, fee, state, pool):
    global window, uname, pwd, worker_state_active, threadpool
    window = win
    uname  = u
    pwd = p
    threadpool = pool
    worker_state_active = state
    window.lineEdit_6.clear()
    window.lineEdit_6.setText('Retrieving fee...')

    # Pass the function to execute
    if not worker_state_active['EST']:
        worker_state_active['EST'] = True
        worker = rpcworker.Worker(get_est, uname, pwd) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)

        # Execute
        threadpool.start(worker)


def print_result(result):
    if err:
        window.lineEdit_6.setText(_translate("MainWindow","No estimate found."))
    else:
        window.lineEdit_6.setText(_translate("MainWindow",str(format(round(float(result),8),'.8f'))))
        window.lineEdit_3.setText(_translate("MainWindow",str(format(round(float(result),8),'.8f'))))
        #fee = result
    worker_state_active['EST'] = False
    return result
    
