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
    
def retrieve():
    global err, err_2

    try:
        cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')


        if not err:
            try:
                cmd_2 = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet getwalletseed"
                result_2, err_2 = (subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                result_2 = result_2.decode('utf-8')
                err_2 = err_2.decode('utf-8')

                if not err_2:
                    return result_2
                else:
                    print('Error:', err_2)
                    return "Failed to retrieve wallet seed. This is likely a legacy wallet."
            except subprocess.CalledProcessError as e:
                msg = "Failed to retrieve wallet seed. This is likely a legacy wallet."
                print(msg, e.output)
                return msg
        else:
            if "ErrWrongPassphrase" in err:
                msg = "Incorrect password entered."
                print(msg, err)
    except subprocess.CalledProcessError as e:
        msg = "Failed to unlock wallet."
        print(msg, e.output)


def execute(u, p, pp, win, state): #, pool
    global window, uname, pwd, worker_state_active, passphrase
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    #threadpool = pool
    passphrase = pp

    return retrieve()
