import subprocess, os, sys, json, threading, signal, traceback, addresses
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from rpcworker import progress_fn, thread_complete, Worker, WorkerSignals
#from resource import resource_path

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
    
def new_addresses_sync(uname, pwd):
    global new_address, pub_key

    new_address = ''
    pub_key = ''

    try:
        #cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet getnewaddress"
        #new_address = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]).decode("utf-8")
        new_address = (subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'getnewaddress'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]).decode("utf-8")
        if new_address:
            pubkey_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet validateaddress " + new_address
            try:
                pub_key = json.loads(subprocess.Popen(resource_path(pubkey_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0])["pubkey"]
                #pub_key = (json.loads(subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'validateaddress', new_address], shell=False, stdout=subprocess.PIPE).communicate()[0]))["pubkey"]
                print(pub_key)
            except subprocess.CalledProcessError as e:
                print(e.output)
        else:
            print('Failed to create new addresses')

    except subprocess.CalledProcessError as e:
        print('Failed to create new addresses', e.output)

    return new_address, pub_key

def new_addresses(uname, pwd, progress_callback):
    global new_address, pub_key

    new_address = ''
    pub_key = ''
    try:
        cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet getnewaddress"
        new_address = (subprocess.Popen(resource_path(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]).decode("utf-8")
        #new_address = (subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'getnewaddress'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]).decode("utf-8")

        if new_address:
            pubkey_cmd = "bin/btcctl -u "+  uname +" -P "+ pwd +" --wallet validateaddress " + new_address
            try:
                pub_key = json.loads(subprocess.Popen(resource_path(pubkey_cmd), shell=True, stdout=subprocess.PIPE).communicate()[0])["pubkey"]
                #pub_key = json.loads(subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet','validateaddress', new_address], shell=False, stdout=subprocess.PIPE).communicate()[0])#["pubkey"]
                #pub_key = pub_key["pubkey"]
            except subprocess.CalledProcessError as e:
                print(e.output)

        else:
            print('Failed to create new addresses')

    except subprocess.CalledProcessError as e:
        print('Failed to create new addresses', e.output)

    return new_address, pub_key

def get_new_address(u, p, win, state, pool):
    global window, uname, pwd, worker_state_active, threadpool
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool

    # Pass the function to execute
    if not worker_state_active['GET_NEW_ADDRESS']:
        worker_state_active['GET_NEW_ADDRESS'] = True
        print_address(new_addresses_sync(uname, pwd))


def print_address(list):
    window.address_line.setText(list[0])
    window.pubkey_line.setText(list[1])
    window.pubkey_line.repaint()
    window.pubkey_line.setCursorPosition(0)
    worker_state_active['GET_NEW_ADDRESS']= False
    addresses.get_addresses(uname, pwd, window, "addresses", worker_state_active, threadpool)
