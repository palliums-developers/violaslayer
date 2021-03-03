# violaslayer
Btc Protocol parsing

# depends
bitcoind:[https://github.com/bitcoin/bitcoin.git] 

## mongodb(version >= 4.0)
install mongodb:[https://docs.mongodb.com/v4.0/tutorial/install-mongodb-on-ubuntu/]

## pymongo(version >= 3.6.3)
pymongo:[https://api.mongodb.com/python/current/installation.html]
python3 -m easy_install pymongo

## numpy
python3 -m pip install numpy

## struct
python3 -m pip install struct

## bitcoinrpc(v0.3.1)

python3 -m pip install [bitcoinrpc](https://pypi.org/project/bitcoinrpc/)

## bitcoind(version >= 0.18)
full-nodes bitcoin
## python3.6.9 or up

# install
git clone [https://github.com/palliums-developers/violaslayer]
cd violaslayer
python3 manage.py --mod "filter"


#webserver
bitcoin transaction query; transaction create and send(use wallet).

you want to use sendtoaddress function must be import account address

ex:
  ./bitcoin-cli --testnet importaddress 2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY
