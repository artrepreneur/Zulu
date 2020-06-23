# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from rpcworker import progress_fn, thread_complete
from dropdowns import refresh_all
from pixMp import *
from config import MIN_CONF, MAX_CONF
import time

_translate = QCoreApplication.translate

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def fold_it(progress_callback):
    balance = float(get_balance())
    lft_ovr_bal = balance
    details = ''
    while not balance < 1:  
        try:
        
            # unlock
            cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
            result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            result = result.decode('utf-8')
            err = err.decode('utf-8')

            # Send
            if not err:
                cmd_2 = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet sendfrom " + to + " 0 '[\"" + fr + "\"]' 1"
                result_2, err_2 = (subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                result_2 = result_2.decode('utf-8')
                err_2 = err_2.decode('utf-8')
                

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
                    print('Transaction Id:',result_2)    
                    # Relock wallet.
                    result_lock, err_lock = subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'walletlock'], shell=False, stdout=subprocess.PIPE).communicate()

                    try:
                        cmd_3 = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet gettransaction " + result_2 + " true"
                        result_3, err_3 = subprocess.Popen(resource_path(cmd_3), shell=True, stdout=subprocess.PIPE).communicate()
                        
                        if not err_3:
                            hex = json.loads(result_3)["hex"]
                            fee = str(format(round(float(json.loads(result_3)["fee"]), 8), '.8f'))
                            amount = str(format(round(float(json.loads(result_3)["amount"]), 8), '.8f'))
                            details += '\n\nYou folded to address: ' + to + '\nAmount: ' + amount + ' PKT\n'

                            # Append results
                            details += 'Transaction ID:' + result_2
                            trns_list.append(details)
                            print('Details:', details)
                            return details

                        else:
                            print('Error:', err_3)
                            return err_3

                    except subprocess.CalledProcessError as e:
                        print('Error:', e.output)


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

        balance = float(get_balance())
        time.sleep(30)
        print('Balance:', balance, 'Left over balance:', lft_ovr_bal)
        while (lft_ovr_bal > 1 and round(balance,0) == 0):
            time.sleep(30)
            balance = float(get_balance())
            print('Balance:', balance, 'Left over balance:', lft_ovr_bal)
            
    return details

   
def get_balance():
    bal_cmd_result = json.loads(subprocess.Popen([resource_path("bin/btcctl"), '-u', uname, '-P', pwd, '--wallet', 'getaddressbalances', MIN_CONF], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])

    for i, item in enumerate(bal_cmd_result):
        address = item["address"]

        if address.strip() == fr.strip():
            balance = format(round(float(item["total"]), 8), '.8f')
            print('Address Balance:', balance)
            return balance

def execute(u, p, win, state, pool, pp, f, t):
    global uname, pwd, window, worker_state_active, threadpool, fr, to, passphrase, bal, trns_list
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    fr = f
    to = t
    threadpool = pool
    passphrase = pp
    trns_list = []

    if not worker_state_active['FOLD_WALLET']:
        worker_state_active['FOLD_WALLET'] = True
        worker = rpcworker.Worker(fold_it)
        worker.signals.result.connect(fold_response_2)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)
        threadpool.start(worker)


def fold_response(result):

    window.lineEdit_7.setText(result)

    # Relock wallet.
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

                    window.textEdit_4.setText(details.strip())
                    window.stackedWidget.setCurrentIndex(window.stackedWidget.indexOf(window.sent_page))

                else:
                    print('Error:', err_4)
                    details = "Could not get transaction details."
                    window.textEdit_4.setText(_translate("MainWindow", details))

            else:
                print('Error:', err_3)
                details = "Could not get transaction details."
                window.textEdit_4.setText(_translate("MainWindow",details))

        except subprocess.CalledProcessError as e:
            print('Error:', e.output)

    else:
        details = "Could not fold. Balance could be too small."
        window.label_77.setText(_translate("MainWindow", details))

    worker_state_active['FOLD_WALLET'] = False


def fold_response_2(result):
    window.lineEdit_7.setText("Transaction ID\'s listed below.")
    window.textEdit_4.setText(_translate("MainWindow",result))
    worker_state_active['FOLD_WALLET'] = False
    window.stackedWidget.setCurrentIndex(window.stackedWidget.indexOf(window.sent_page))
