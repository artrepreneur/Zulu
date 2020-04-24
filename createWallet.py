import subprocess, os, sys, json
#import pexpect
import time
#from resource import resource_path

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def seed_execute(uname, pwd, pp, old_pass_line, seed_entry):
    try:
        cmd_result, err = subprocess.Popen(resource_path("bin/pktwallet -u "+uname+" -P "+pwd+" --create"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(("{\"passphrase\":\""+pp+"\",\"seed\":\""+ seed_entry +"\",\"seedpassphrase\":\""+old_pass_line+"\"}").encode('utf-8'))
        err = err.decode('utf-8')
        #print('cmd_result', cmd_result)

        if err:
            print('Error:', err)
            cmd_result = {}
        else:
            cmd_result = json.loads(cmd_result.decode('utf-8'))

        return cmd_result
    except:
        print("Could not create wallet")
        return {}


def execute(uname, pwd, pp):
    try:
        cmd_result, err = subprocess.Popen(resource_path("bin/pktwallet -u "+uname+" -P "+pwd+" --create"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(("{\"passphrase\":\""+pp+"\"}").encode('utf-8'))
        err = err.decode('utf-8')
        print(cmd_result, err)

        if err and not cmd_result:
            print('Error:', err)
            cmd_result = {}
        else:
            cmd_result = json.loads(cmd_result.decode('utf-8'))

        return cmd_result
    except:
        print("Could not create wallet")
        return {}
