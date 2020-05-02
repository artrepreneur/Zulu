# PKT Cash Wallet
PKT Cash wallet is a QT wallet for the PKT Cash blockchain mainnet. This wallet adds a graphical user interface (GUI) to the command line daemon [pktwallet](https://github.com/pkt-cash/pktd/tree/master/pktwallet). PKT Cash Wallet runs as a standalone application for macOS currently, and eventually will have support for Unix. 

This is a full node wallet and not SPV at this time. It comes bundled with binaries for a full node daemon [pktd](https://github.com/pkt-cash/pktd), [pktwallet](https://github.com/pkt-cash/pktd/tree/master/pktwallet), and the remote procedure call (RPC) client [btcctl](https://github.com/pkt-cash/pktd/tree/master/cmd/btcctl). These binaries are stored in the bin folder of this repo. It is also possible to compile these binaries from their respective repositories. These binaries should be placed in the bin folder or the wallet will cease to work.     

## Wallet Features
The wallet includes the following features. 

1. Send and receive transactions.
2. Sign transactions.
3. Verify transactions.
4. Generate new regular addresses and new multisig addresses.
5. Create multisig transactions.
6. Export private keys and import new private keys.
7. Password-protect the wallet.
8. Save and restore the wallet backup from seed.
9. Fold wallet addresses - for large UTXO sets.
10. View full transaction history.

# Installation
Clone the repository.

```
git clone https://github.com/artrepreneur/PKT-Cash-Wallet
```

Please use Python 3. Create an [Anaconda](https://www.anaconda.com/products/individual) environment.

Install PyQt5

```
pip install PyQt5
```

Install `zbar`. The zbar DLLs are included with the Windows Python wheels. However, you will need to install the `zbar` shared library on other operation systems

Mac OS X:

```
brew install zbar
```
Linux:

```
sudo apt-get install libzbar0
```

Use pip to install the dependencies from requirements.txt. 

```
pip install -r requirements.txt
```

## Running PKT Cash Wallet

To run PKT Cash wallet, just invoke the python script as follows. 

```
python PKTWallet.py
```

That's it. If you have a legacy command line wallet already running it will use the existing wallet database already present on your system. If you don't have a command line wallet you will be prompted to create a new wallet. Always, make sure to store your wallet seed in a safe place. 
