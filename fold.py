# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
#from resource import resource_path
from rpcworker import progress_fn, thread_complete
from dropdowns import refresh_all
from pixMp import *
from config import MIN_CONF, MAX_CONF

_translate = QCoreApplication.translate

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def fold_it(progress_callback):

    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if not err:
            cmd_2 = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet sendfrom " + to + " 0 '[\"" + fr + "\"]' 1"
            result_2, err_2 = (subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            result_2 = result_2.decode('utf-8')
            err_2 = err_2.decode('utf-8')
            print(result_2, err_2)

            if err_2:
                print("Error:", err_2)
                if "waddrmgr.scriptAddress" in err_2:
                    window.label_77.setText(_translate("MainWindow","You are using a multisig sending address. You must use \"create multisig\" option under menu."))
                elif "InsufficientFundsError" in err_2:
                    window.label_77.setText(_translate("MainWindow","Either you do not have sufficient balance, or you recently submitted a transaction and must wait for it to clear."))
                else:
                    msg = "Failed to fold. "
                    window.label_77.setText(_translate("MainWindow",msg))
                worker_state_active['FOLD_WALLET'] = False
                exit()
            else:
                return result_2

        else:
            msg = "Could not unlock wallet."
            print(msg, err)
            window.label_77.setText(_translate("MainWindow",msg))
            worker_state_active['FOLD_WALLET'] = False
            exit()

    except subprocess.CalledProcessError as e:
        print('Failed to unlock wallet.', e.output)
        worker_state_active['FOLD_WALLET'] = False
        exit()



def execute(u, p, win, state, pool, pp, f, t):
    global uname, pwd, window, worker_state_active, threadpool, fr, to, passphrase
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    fr = f
    to = t
    threadpool = pool
    passphrase = pp

    if not worker_state_active['FOLD_WALLET']:
        worker_state_active['FOLD_WALLET'] = True

        worker = rpcworker.Worker(fold_it)
        worker.signals.result.connect(fold_response)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)
        threadpool.start(worker)


def fold_response(result):
    window.lineEdit_7.setText(result)

    # Relock wallet.
    #lock = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
    #result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()
    result_lock, err_lock = subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'walletlock'], shell=False, stdout=subprocess.PIPE).communicate()

    if result:
        try:
            cmd_3 = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet gettransaction " + result
            result_3, err_3 = subprocess.Popen(resource_path(cmd_3), shell=True, stdout=subprocess.PIPE).communicate()
            
            if not err_3:
                hex = json.loads(result_3)["hex"]
                fee = str(format(round(float(json.loads(result_3)["fee"]), 8), '.8f'))
                cmd_4 = "bin/btcctl -u "+  uname +" -P "+ pwd +" decoderawtransaction " + hex
                result_4, err_4 = subprocess.Popen(resource_path(cmd_4), shell=True, stdout=subprocess.PIPE).communicate()

                if not err_4:
                    vout = json.loads(result_4)["vout"]
                    sender = fr
                    balance = 0
                    deet = ''
                    for i in range(0, len(vout)):
                        addr = vout[i]['scriptPubKey']['addresses'][0]
                        amount = str(round(float(vout[i]['value']),8))
                        if not(addr.strip() == sender):
                            deet += 'You folded to address: ' + addr + '\nAmount: ' + amount + ' PKT\n\n'
                        else:
                            balance += amount

                    details = deet
                    details += 'Your fees were: ' + fee + ' PKT'
                    window.textEdit_4.setText(details.strip())
                    window.stackedWidget.setCurrentIndex(window.stackedWidget.indexOf(window.sent_page))
                else:
                    print('Error:', err_4)
                    window.textEdit_4.setText(_translate("MainWindow","Could not get transaction details."))

            else:
                print('Error:', err_3)
                window.textEdit_4.setText(_translate("MainWindow","Could not get transaction details."))

        except subprocess.CalledProcessError as e:
            print('Error:', e.output)

    else:
        window.label_77.setText(_translate("MainWindow","Could not fold. Balance could be too small."))

    worker_state_active['FOLD_WALLET'] = False
