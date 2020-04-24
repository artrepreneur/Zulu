from electrum.util import bh2u
from electrum.bitcoin import base_decode
from electrum.transaction import Transaction
from electrum.transaction import tx_from_str

def combine_transactions(transaction_bin):
    transactions = list(
        map(lambda tx_bin: Transaction(tx_from_str(tx_bin)), transaction_bin))
    tx0 = transactions[0]
    tx0.deserialize(True)
    return tx0

def combine(uname, pwd, window, trans_list):

    try:
        tx = combine_transactions(trans_list)
        inputs = tx.inputs()
        serialized = tx.serialize_to_network()
        return serialized

    except:
        return "Unable to combine transactions. Check if transaction and/or all signatures are valid."
