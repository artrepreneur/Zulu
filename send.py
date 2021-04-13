# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
#from resource import resource_path
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate
from config import MIN_CONF, MAX_CONF

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def execute2(u, p, a, pp, pd, win, state):
    global window, uname, pwd, worker_state_active, address, pay_dict, passphrase
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    address = a
    passphrase = pp
    pay_dict = pd
    window.label_6.clear()

    try:
        cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 1000'
        result, err = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if not err:
            amount = 0
            payments = ''
           

            for i, item in enumerate(pay_dict):
                item = str(item)
                payments += item + ' ' + str(pay_dict[item])
                amount += float(pay_dict[item])
                if not len(pay_dict) == (i + 1):
                    payments +=', '

            cmd = " " + payments + " '[" + '"' + address + '"' + "]'"
             
            try:     
                    cmd_2 = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet sendfrom" + cmd + " 1"
                    print(cmd_2)                    
                    result_2, err_2 = subprocess.Popen(resource_path(cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                    result_2 = result_2.decode('utf-8')
                    err_2 = err_2.decode('utf-8')
                    print(result_2, err_2)

                    if not err_2:
                        print('Transaction ID:', result_2)
                        window.lineEdit_7.clear()
   
                        # Relock wallet.
                        lock = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
                        subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()
                        window.lineEdit_7.setText(result_2)

                        try:
                            cmd_3 = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet gettransaction " + result_2 + " true"
                            result_3, err_3 = subprocess.Popen(resource_path(cmd_3), shell=True, stdout=subprocess.PIPE).communicate()
                            
                            if not err_3:
                                hex = json.loads(result_3)["hex"]
                                fee = str(format(round(float(json.loads(result_3)["fee"]), 8), '.8f'))
                                details = json.loads(result_3)["details"]
                                deet = ''
                                print('Transaction details:', details)
                                
                                '''
                                for item in details:
                                    if (item["category"] == "receive"):
                                        addr = item["address"]
                                        amount = str(format(round(float(item["amount"]), 8), '.8f'))
                                        deet += 'You sent address: ' + addr + '\nthe amount: ' + amount + ' PKT\n\n'
                                '''

                                for i, item in enumerate(pay_dict):
                                    deet += 'You sent address: ' + str(item) + '\nthe amount: ' + str(pay_dict[item]) + ' PKT\n\n'         
                                 
                                deet += 'Your fees were: ' + fee + ' PKT'
                                window.textEdit_4.setText(deet.strip())
                                window.stackedWidget.setCurrentIndex(window.stackedWidget.indexOf(window.sent_page))

                            else:
                                print('Error:', err_3)
                                window.textEdit_4.setText(_translate("MainWindow","Could not get transaction details."))

                        except subprocess.CalledProcessError as e:
                            print('Error:', e.output)

                    else:
                        print('Error:', err_2)
                        if "waddrmgr.scriptAddress" in err_2:
                            window.label_6.setText(_translate("MainWindow","You are using a multisig sending address. You must use \"create multisig\" option under menu."))
                        elif "ErrRejectDust" in err_2:
                            window.label_6.setText(_translate("MainWindow","Transaction too small error."))
                        elif "InsufficientFundsError" in err_2:
                            window.label_6.setText(_translate("MainWindow","You have insufficient balance. Wait for a past transaction to confirm or fold your address."))
                        elif "RejInsufficientFee" in err_2:
                            window.label_6.setText(_translate("MainWindow","Insufficient fees error."))
                        elif "ErrOrphanTransactionDisallowed" in err_2:
                            window.label_6.setText(_translate("MainWindow","This transaction references and orphan output, try to resync."))
                        elif "TooManyInputsError:" in err_2:
                            window.label_6.setText(_translate("MainWindow","To complete this transaction you will need to fold all balances from this address."))
                        else:
                            window.label_6.setText(_translate("MainWindow","Unable to submit transaction. Make sure all payees have a valid address and amount."))

            except subprocess.CalledProcessError as e:
                print('Failed to submit transaction', e.output)
        else:
            if "ErrWrongPassphrase" in err:
                print('Incorrect password.',err)
                window.label_6.setText(_translate("MainWindow","Incorrect password."))

    except subprocess.CalledProcessError as e:
        print('Failed to unlock wallet.', e.output)
    
    worker_state_active['SEND_PAY'] = False
