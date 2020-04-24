import subprocess
import os, sys
from PyQt5.QtCore import *
#from resource import resource_path
from config import MIN_CONF, MAX_CONF
_translate = QCoreApplication.translate

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def get_balance(uname, pwd):
    bal_cmd_result, err = (subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'getbalance'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    bal_cmd_result = bal_cmd_result.decode('utf-8')
    err = err.decode('utf-8')

    if not err:
        bal_cmd_result = round(float(bal_cmd_result),8)
        return str(bal_cmd_result).rstrip()

def get_balance_for_addr(uname, pwd, addr):
    addr_bal_cmd_result, err = (subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'listunspent', MIN_CONF, MAX_CONF, '[\"'+addr+'\"]'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    addr_bal_cmd_result = addr_bal_cmd_result.decode('utf-8')
    err = err.decode('utf-8')

    if not err:
        bal = 0
        for itm in addr_bal_cmd_result:
            tmp_bal = round(float(itm["amount"]),4)
            bal += tmp_bal
        return str(bal)
