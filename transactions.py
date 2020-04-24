import subprocess, os, sys, json, threading, signal, traceback, rpcworker
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from datetime import datetime
from rpcworker import progress_fn, thread_complete
_translate = QCoreApplication.translate
#from resource import resource_path
#from pixMp import *

def resource_path(relative_path):
    #dir = QDir.currentPath()
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def get_history(uname, pwd, progress_callback):
    global err, count, state
    count = 100
    state = int(page) * (count -1)

    try:
        result, err = subprocess.Popen([resource_path('bin/btcctl'), '-u', uname, '-P', pwd, '--wallet', 'listtransactions', str(count), str(state)], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        result = json.loads(result)
        err = err.decode('utf-8')
        if err:
            print('Error:', err)
        return result

    except subprocess.CalledProcessError as e:
        print('Failed to retrieve public key.', e.output)

def history(u, p, pg, win, state, pool):
    global window, uname, pwd, worker_state_active, page
    window = win
    uname  = u
    pwd = p
    worker_state_active = state
    threadpool = pool
    page = pg

    # Pass the function to execute
    if not worker_state_active['TRANS']:
        worker_state_active['TRANS'] = True
        worker = rpcworker.Worker(get_history, uname, pwd)
        worker.signals.result.connect(print_result)
        worker.signals.finished.connect(thread_complete)
        worker.signals.progress.connect(progress_fn)
        threadpool.start(worker)

def row_count(iterator):
    count = 0
    if iterator.value():
        while iterator.value():
            item = iterator.value()
            if item.parent():
                if item.parent().isExpanded():
                    count +=1
            else:
                count += 1
            iterator += 1
        if item.text(0).strip()=='Loading...' :
            count = 0
            window.transaction_hist_tree.clear()
    #print('count', count)        
    return count

def print_result(result):
    #print('result', result)
    if result:
        iterator = QtWidgets.QTreeWidgetItemIterator(window.transaction_hist_tree)
        count = row_count(iterator)


        for i, item in enumerate(result):
                index = (count) + i
                #print(i, index, item)
                time = item["time"]
                ts = str(datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))
                address = item["address"]
                amount = str(round(item["amount"],8)) + ' PKT'
                trans_id = item["txid"]

                item_0 = QtWidgets.QTreeWidgetItem(window.transaction_hist_tree)
                font = QFont()
                font.setFamily("Helvetica")
                font.setPointSize(15)
                item_0.setFont(0, font)
                item_0.setFont(1, font)
                item_0.setFont(2, font)
                item_0.setFont(3, font)
                #print(ts, address, amount, trans_id)
                window.transaction_hist_tree.setStyleSheet("QTreeView::item { padding: 5px }")
                window.transaction_hist_tree.topLevelItem(index).setText(0, _translate("MainWindow", ts))
                window.transaction_hist_tree.topLevelItem(index).setText(1, _translate("MainWindow", address))
                window.transaction_hist_tree.topLevelItem(index).setText(2, _translate("MainWindow", amount))
                window.transaction_hist_tree.topLevelItem(index).setText(3, _translate("MainWindow", trans_id))
                window.transaction_hist_tree.repaint()        
    else:
        item_0 = QtWidgets.QTreeWidgetItem(window.transaction_hist_tree)
        window.transaction_hist_tree.topLevelItem(0).setText(0, _translate("MainWindow", "No transactions found."))

    worker_state_active['TRANS'] = False
