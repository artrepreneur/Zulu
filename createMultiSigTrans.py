import subprocess, os, sys, json
from PyQt5.QtCore import *
from PyQt5 import QtWidgets


_translate = QCoreApplication.translate
MIN_CONF = '1'
MAX_CONF = '9999999'
#USE_RAW_TRANS = False
TRANS_RATE = 1
PUB_KEY_SIZE = 33

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def create_tr(uname, pwd, fee, redeem_script, addr_arr, from_addr): #amount

    outs = len(addr_arr)

    # Get all UTXO's you need to make the transaction happen.
    chk_bal_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet listunspent " + MIN_CONF + " " + MAX_CONF + " '[" + '"'+ from_addr + '"' + "]'"
    chk_bal_result, err = (subprocess.Popen(resource_path(chk_bal_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    chk_bal_result = json.loads(chk_bal_result.decode('utf-8'))
    err = err.decode('utf-8')
    print(chk_bal_cmd,'\n', chk_bal_result)

    if err or chk_bal_result == []:
        print('Error:', err)
        window.label_65.setText("Error: Not enough balance in "+from_addr)
        msg = "Error: Not enough balance in "+from_addr
        return msg

    else:
        bal = 0
        trans_arr = []

        # Sends to an array of addresses
        amount = 0
        send_to_raw = " '{"
        for i, key in enumerate(addr_arr): #Calc total amount to send
            tmp_bal = round(float(addr_arr[key]),8)
            send_to_raw += '"' + key + '":' + str(tmp_bal)
            if i != (len(addr_arr) - 1):
                send_to_raw +=', '
            amount += tmp_bal

        amount = round(float(amount),8)

        # Calc amount address has as bal
        for itm in chk_bal_result:
            tmp_bal_2 = round(float(itm["amount"]),8)
            bal += tmp_bal_2
            trans_arr.append({"txid":itm["txid"], "vout": itm["vout"], "amount": str(tmp_bal_2), "scriptPubKey":itm["scriptPubKey"]})
            if bal >= amount:
                break

        ins = len(trans_arr)
        bal = round(float(bal),8)        
        print('amount to pay:', amount, 'pay with balance:', bal)

        # If you do not have enough balance to make the sending amount.
        if bal < amount:
            window.label_65.setText("Transaction failed2. Check that your multisig account has enough funds.")
            return "Error: Transaction failed. Check that your multisig account has enough funds."

        else:
            # Assemble all inputs needed
            inputs ="'["
            for i, itm in enumerate(trans_arr):
                print ('{:=<100}'.format(''))
                inputs +='{' + '"txid":' + '"' + itm["txid"] +'",' + '"vout":' + str(itm["vout"]) + ',' + '"scriptPubKey":' + '"' + itm["scriptPubKey"] + '",' + '"redeemScript":' + '"' + redeem_script +'"}'
                if i != (len(trans_arr) - 1):
                    inputs += ','
            inputs +="]'"

            print('inputs', inputs)

             # calc fees dynamically
            m = int(required_sigs)
            n = len(pubKeys.split(','))
            size_of_redeem_script = n + (n * PUB_KEY_SIZE) + 3
            script_sig_size = 2 + (74 * m) + size_of_redeem_script
            input_size = script_sig_size + 5 + (36 * ins)
            trans_size = input_size + (2 * ins) + 4 + (34 * outs)
            dynamic_fee = round((trans_size * TRANS_RATE * .00000001), 8)

            if dynamic_fee > round(float(fee),8):
                fee = dynamic_fee
            print('accurate fee:', fee)

            # Adds on the change balance address
            change = round((float(bal) - float(amount) - float(fee)), 8)

            if change > 0:
                send_to_raw += ', "' + from_addr + '":' + str(change)
            send_to_raw += "}'"
            trans_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" createrawtransaction " + inputs + send_to_raw
            print('create_raw_trans:', trans_cmd)

            # unlock wallet
            create_raw_result, err = (subprocess.Popen(resource_path(trans_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            create_raw_result = create_raw_result.decode('utf-8')
            err = err.decode('utf-8')

            print('create_raw_result',create_raw_result)
            if err:
                print('Error:', err)
                window.label_65.setText("Error: Transaction could not be created.")
                msg = "Error: Transaction could not be created." + err
                return msg

            else:

                if create_raw_result == '':
                    print('Raw Transaction Empty.')
                    window.label_65.setText("Raw Transaction Empty.")
                    msg = "Raw Transaction Empty."
                    return msg

                else:
                    return create_raw_result

def create(uname, pwd, amount, from_addr, addr_arr, fee, passphrase, window):
    global required_sigs, pubKeys

    fee =  format(round(float(fee),8), '.8f')
    to_addr = next(iter(addr_arr))
    success = False
    redeem_script = ''
    required_sigs = ''
    pubKeys = ''

    try:
        # Access redeemScript file
        try:
            # Try to open if it exists.
            with open('MultisigData/mdata.json', 'r') as infile:
                json_data = json.load(infile)
            json_arr = json_data["addr_data"]

            # import redeemScript and PK's
            for data in json_arr:
                if data["multisigAddress"] == from_addr:
                    redeem_script = data["redeemScript"]
                    required_sigs = int(data["requiredSigs"])
                    pubKeys = data["pubKeys"]
                    success = True
                    break

        except:
            print("no mdata.json file.")

        if not success:
            unlock_cmd = 'bin/btcctl -u ' + uname + ' -P ' + pwd + ' --wallet walletpassphrase ' + passphrase + ' 1000'
            unlock_result, err = (subprocess.Popen(resource_path(unlock_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
            unlock_result = unlock_result.decode('utf-8')
            err = err.decode('utf-8')
            print('unlock:', unlock_result, err)

            if err:
                print('Error:', err)
                msg = "Error: Wallet passphrase failed. " + err
                window.label_65.setText(msg)
                return msg

            else:
                create_trans = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet createtransaction " + to_addr + " " +  str(amount) + " '[" + '"'+ from_addr + '"' + "]'"
                print('create_trans', create_trans)
                create_trans_result, err = (subprocess.Popen(resource_path(create_trans), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                create_trans_result = create_trans_result.decode('utf-8')
                err = err.decode('utf-8')
                print('create_trans_result', create_trans_result, err)

                if err:
                    print('Error:', err)
                    if 'InsufficientFundsError' in err:
                        window.label_65.setText("Error: Transaction failed. Check that your multisig account has enough funds.")
                        msg = "Error: Transaction failed. Check that your multisig account has enough funds."
                    else:
                        window.label_65.setText("Error: Transaction could not be created at this time.")
                        msg = "Error: Transaction could not be created at this time."
                    return msg

                else:
                    return create_trans_result
        else:
            res = create_tr(uname, pwd, fee, redeem_script, addr_arr, from_addr)
            return res    

    except:
        window.label_65.setText("Transaction failed. Check that your multisig account has enough funds.")
        print("Transaction failed.")
        return "Error: Transaction failed. Check that your multisig account has enough funds."
