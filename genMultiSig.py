import subprocess, os, sys, json, threading, signal, traceback, rpcworker, addresses
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
    
# Create new multisig
def new_multisig (uname, pwd, required_sigs, pub_keys, passphrase, progress_callback):
    global e, multisig_result

    base_cmd ='bin/btcctl -u ' + uname + ' -P ' + pwd + ' --wallet '
    multisig_cmd = base_cmd + 'createmultisig ' + required_sigs + pub_keys

    try:
        multisig_result, err = (subprocess.Popen(resource_path(multisig_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        multisig_result = multisig_result.decode('utf-8')
        err = err.decode('utf-8')
        if err:
            print('Error:', err)
            window.label_13.setText("Could not create multisig address, invalid key/s.")
        else:
            multisig_result = json.loads(multisig_result)
            add_new_multisig(uname, pwd, required_sigs, pub_keys, passphrase)
            return multisig_result
    except subprocess.CalledProcessError as e:
        print('Multisig RPC Error:', e.output)

# Add it to the wallet via import
def add_new_multisig (uname, pwd, required_sigs, pub_keys, passphrase):

    base_cmd ='bin/btcctl -u ' + uname + ' -P ' + pwd + ' --wallet '

    # Unlock the wallet first
    unlock_cmd = base_cmd + ' walletpassphrase ' + passphrase + ' 1000'

    try:
        result, err = (subprocess.Popen(resource_path(unlock_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
        result = result.decode('utf-8')
        err = err.decode('utf-8')

        if err:
            print('Error:', err)
            return err 
        else:
            add_cmd = base_cmd + 'addmultisigaddress ' + required_sigs + pub_keys
            try:
                add_result, err = (subprocess.Popen(resource_path(add_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
                add_result = add_result.decode('utf-8')
                err = err.decode('utf-8')
                if err:
                    print('Error:', err)
                    if "ErrRPCInvalidAddressOrKey" in err:
                        err_msg = "Invalid public key/s. " + err
                    return err_msg
                else:
                    return add_result
            except subprocess.CalledProcessError as e:
                print(e.output)
                err_msg = "Invalid public key/s. " + e.output
                return err_msg

    except subprocess.CalledProcessError as e:
        print(e.output)
        err_msg = "Unable to unlock wallet. " + e.output
        return err_msg


def create(u, p, win, ac, aa, pp, state, pool):

    global window, uname, pwd, worker_state_active, passphrase, required_sigs, threadpool, addr_arr, pub_keys
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    passphrase = pp
    addr_arr = aa
    pub_keys =" '["
    required_sigs = str(ac)

    pub_keys =" '["
    for index, item in enumerate(addr_arr):
        key = item
        pub_keys += '"'+ key +'"'
        if index != len(addr_arr)-1:
            pub_keys += ','
    pub_keys +="]'"

    # Pass the function to execute
    if not worker_state_active['GET_MULTI_ADDR']:
        worker_state_active['GET_MULTI_ADDR'] = True
        worker = rpcworker.Worker(new_multisig, uname, pwd, required_sigs, pub_keys, passphrase)
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)

        # Execute
        threadpool.start(worker)

def print_result(result):
    # open success screen, could be msg box
    worker_state_active['GET_MULTI_ADDR'] = False

    if result:
        addrs = ', '.join(addr_arr)
        multi_addr = result["address"]
        redeem_script = result["redeemScript"]

        dict = {"addr_data":[]}
        row_arr = dict["addr_data"]
        row = {
            "multisigAddress":multi_addr,
            "redeemScript":redeem_script,
            "requiredSigs":required_sigs,
            "pubKeys":addrs
        }

        try:
            json_data = []
            # Try to open if it exists.
            with open('MultisigData/mdata.json', 'r') as infile:
                line = infile.readline()
                if not line == '':
                    json_data = json.load(infile)
                else:
                    raise Exception('Empty mdata.json file.') 

            if len(json_data) > 0:
                flag = False
                json_arr = json_data["addr_data"]

                # Do an update if you can
                for data in json_arr:
                    if data["multisigAddress"] == str(multi_addr):
                        data["multisigAddress"] = str(multi_addr)
                        data["redeemScript"] = redeem_script
                        data["requiredSigs"] = required_sigs
                        data["pubKeys"] = "["+ addrs +"]"
                        flag = True
                        break

                # No update, just append
                if not flag:
                    json_arr.append(row)

                # Write it back out
                with open('MultisigData/mdata.json', 'w') as outfile:
                    json.dump(json_data, outfile)

        except:
            # No file, write it for the first time.
            print("Creating multisig data file")
            row_arr.append(row)
            with open("MultisigData/mdata.json", 'w') as outfile:
                json.dump(dict, outfile, indent = 4)
        

        i = window.stackedWidget.indexOf(window.multi_sccs_page)
        window.stackedWidget.setCurrentIndex(i)
        window.new_multi_line.setText(_translate("MainWindow",multi_addr))
        window.redeem_txt.setText(_translate("MainWindow",redeem_script))
        addresses.get_addresses(uname, pwd, window, "addresses", worker_state_active, threadpool)
