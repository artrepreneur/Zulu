# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
#from resource import resource_path

_translate = QCoreApplication.translate
MIN_CONF = '1'
MAX_CONF = '9999999'

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def create(uname, pwd, fee, raw_trans, window):
    try:
        min_est_fee = format(round(len(bytes.fromhex(raw_trans)) * .00000001, 8), '.8f')
        if float(min_est_fee) <= 400000:

            # decode the raw transaction and display it during sending for confirmation.
            decode_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" decoderawtransaction " + raw_trans
            result, err = (subprocess.Popen(resource_path(decode_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            result = result.decode('utf-8')
            err = err.decode('utf-8')

            if not err:
                decode_result = (json.loads(result))['vout']
                details = ""
                for item in decode_result:
                    amount = item["value"]
                    pay_to = item["scriptPubKey"]["addresses"][0]
                    details += "Sending: " + str(amount) +  " PKT to: " + str(pay_to) + "\n\n"

                if float(fee) < float(min_est_fee):
                    fee = min_est_fee
                details += "Estimated fees: "+str(format(float(fee), '.8f'))

            msg_box_21 = QtWidgets.QMessageBox()
            msg_box_21.setText('Use "Show Details" to confirm this is the transaction you wish to send. Then click "Send" to submit to network.')
            msg_box_21.setDetailedText(details)
            msg_box_21.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.Cancel)
            snd_multi_btn = msg_box_21.button(QtWidgets.QMessageBox.Yes)
            snd_multi_btn.setText("Send")
            ret = msg_box_21.exec()

            if ret == QtWidgets.QMessageBox.Yes:
                send_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" sendrawtransaction " + str(raw_trans)
                send_result, err = (subprocess.Popen(resource_path(send_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                send_result = send_result.decode('utf-8')
                err = err.decode('utf-8')
                print('err/result:', err, send_result)

                if err:
                    print('Error:', err)
                    msg = 'Error: Failed to send.'
                    if "txn-already-in-mempool" in err:
                        msg = "Error: Could not send transaction. Transaction already sent."
                    elif "ErrOrphanTransactionDisallowed" in err_2:
                        msg = "This transaction references and orphan output, try to resync."
                    else:
                        msg = "Error: Could not send transaction. Make sure you have all required signatures."
                    window.label_66.setText(msg)

                    return {"result":msg + err}
                else:
                    return {"result":send_result, "details":details}

            elif ret == QtWidgets.QMessageBox.Cancel:
                return {"result":"Cancel"}
        else:
            return {"result": "Error: Transaction size too large, too many inputs. Try folding."}
    except:
        window.label_66.setText("Sending failed.")
        return {"result": "Error: Sending failed."}
