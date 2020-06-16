# Copyright (c) 2020 Vishnu J. Seesahai
# Use of this source code is governed by an MIT
# license that can be found in the LICENSE file.

import subprocess
import os, sys, json
#from resource import *

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def get_inf(uname, pwd):
    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet getinfo"
        result, err = subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        result = json.loads(result.decode('utf-8'))
        err = err.decode('utf-8')
        if not err:
            print('Wallet Info:', result)
        if err:
            print('Error:', err)
            result = {}
        return result
    except:
        pass
