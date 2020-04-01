'''

violaslayer config
'''

traceback_limit = 4

#btc connect 
btc_conn = {'rpcuser':'btc', 
        'rpcpassword':'btc', 
        'rpcip':'127.0.0.1', 
        'rpcport':18332}

#db info type(vfilter vfilter lfilter v2b  l2b v2l)
db_list=[
        #remote
        {'host':'127.0.0.1', 'port':37017, 'db':'base','user':'violas', 'password':'violas@palliums'},
        {'host':'127.0.0.1', 'port':37017, 'db':'proof','user':'violas', 'password':'violas@palliums'},
        {'host':'127.0.0.1', 'port':37017, 'db':'addresses','user':'violas', 'password':'violas@palliums'},
        ]

looping_sleep={
        'bfilter' : 1,
        'comm': 8,          #communication thread loop time
        }
