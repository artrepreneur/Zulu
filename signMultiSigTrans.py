# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess, os, sys, json #threading, signal, traceback, rpcworker
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
    
def create(uname, pwd, raw_trans, passphrase, window):

    try:
        # unlock wallet
        unlock_cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletpassphrase " + passphrase + ' 10000'
        result, err = (subprocess.Popen(resource_path(unlock_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')
        print('unlock', result)

        # init
        txid = ''
        vout = ''
        redeem_script = ''
        scriptpubkey = ''
        sender_addr = ''

        if err:
            print('Error:', err)
            window.label_66.setText("Error: Wallet could not be unlocked. Check your wallet passphrase.")

        else:
            decode_cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" decoderawtransaction " + raw_trans
            print('decode command', decode_cmd)
            result, err = (subprocess.Popen(resource_path(decode_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            result = result.decode('utf-8')
            err = err.decode('utf-8')
            #print('res', result)

            if not err:
                json_trans = json.loads(result)
                decode_result = (json_trans)['vout']
                print('decoded trans:', decode_result)

                # Get sender.
                txid = (json_trans)['vin'][0]["txid"]
                vout = (json_trans)['vin'][0]["vout"]
                print('txid', txid, 'vout', vout)
                sender_cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" getrawtransaction " + txid
                print(sender_cmd)
                sndr_result, sndr_err = (subprocess.Popen(resource_path(sender_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                sndr_result = sndr_result.decode('utf-8')
                sndr_err = sndr_err.decode('utf-8')
                print('sender res', sndr_result, sndr_err) 

                if not sndr_err:
                    decode_cmd_2 = "bin/pktctl -u "+  uname +" -P "+ pwd +" decoderawtransaction " + sndr_result
                    result_2, err_2 = (subprocess.Popen(resource_path(decode_cmd_2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                    result_2 = result_2.decode('utf-8')
                    err_2 = err_2.decode('utf-8')

                    if not err_2:    
                        json_trans_2 = json.loads(result_2)
                        decode_result_2 = (json_trans_2)['vout']
                        for item in decode_result_2:
                            if item["n"] == vout:
                                sender_addr = item["address"]
                                print("Sender:", sender_addr)

                        # Get some details for confirmation            
                        details = ''
                        for item in decode_result:
                            amount = item["value"]
                            pay_to = item["scriptPubKey"]["addresses"][0]
                            details += "Sending: " + str(amount) +  " PKT to: " + str(pay_to) + "\n\n"
                        
                            if pay_to == sender_addr:
                                scriptpubkey = item["scriptPubKey"]["hex"]

                        msg_box_24 = QtWidgets.QMessageBox()
                        msg_box_24.setText('Use "Show Details" to confirm this is the transaction you wish to sign. Then click "ok" to sign it.')
                        msg_box_24.setDetailedText(details)
                        msg_box_24.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.Cancel)
                        snd_multi_btn = msg_box_24.button(QtWidgets.QMessageBox.Yes)
                        snd_multi_btn.setText("Ok")
                        ret = msg_box_24.exec()

                        if ret == QtWidgets.QMessageBox.Yes:

                            #try:
                            # Try to open if it exists.
                            with open('MultisigData/mdata.json', 'r') as infile:
                                json_data = json.load(infile)
                            json_arr = json_data["addr_data"]

                            # import redeemScript and PK's
                            for data in json_arr:
                                if data["multisigAddress"] == sender_addr:
                                    redeem_script = data["redeemScript"]
                                    success = True
                                    break
                        

                            sign_cmd = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet signrawtransaction " + str(raw_trans) + " '[{\"txid\":\""+str(txid)+"\",\"n\":\""+str(vout)+"\",\"scriptpubkey\":\""+str(scriptpubkey)+"\",\"redeemscript\":\""+str(redeem_script)+"\"}]'"
                            print(sign_cmd)

                            sign_result, err_3 = (subprocess.Popen(resource_path(sign_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                            sign_result = sign_result.decode('utf-8')
                            err_3 = err_3.decode('utf-8')
                            signed_trans = str(json.loads(sign_result)['hex'])
                            print(signed_trans)

                            # Relock wallet.
                            lock = "bin/pktctl -u "+  uname +" -P "+ pwd +" --wallet walletlock"
                            result_lock, err_lock = subprocess.Popen(resource_path(lock), shell=True, stdout=subprocess.PIPE).communicate()

                            if err_3:
                                print('Error:', err_3)
                                window.label_66.setText("Error: Could not create transaction. Try again.")
                                return "Error: Could not sign transaction. Try again. " + err_3

                            else:
                                return signed_trans    

                            #except:
                            #    print("No mdata.json file present.")
                            #    return "Error: Could not sign transaction." 

                        elif ret == QtWidgets.QMessageBox.Cancel:
                            return
                    else:
                        raise Exception("Signing failure") 
                else:
                    print("Signing failure", sndr_err)
                    window.signed_text.setText("Signing failure:" + sndr_err)
                    raise Exception("Signing failure")            
    
    except:
        window.label_66.setText("Signing failed.")
        print("Signing failed.")
        return "Error: Signing failed."
        
