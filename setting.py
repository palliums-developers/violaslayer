'''

violaslayer config
'''

traceback_limit = 4

#btc connect 
btc_conn = {'rpcuser':'btc', 'rpcpassword':'btc', 'rpcip':'127.0.0.1', 'rpcport':18332}

#db info type(bfilter)
db_list=[
        #remote
        {'host':['127.0.0.1:37017'], 'db':'base','user':'violas', 'password':'violas@palliums', 'authdb' : 'admin', 'rsname':'rsviolas'},
        {'host':['127.0.0.1:37017'], 'db':'b2vproof','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
        {'host':['127.0.0.1:37017'], 'db':'markproof','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
        {'host':['127.0.0.1:37017'], 'db':'addresses','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
        ]

looping_sleep={
        'bfilter' : 10,
        'b2vproof' : 10,
        'comm': 80,          #communication thread loop time
        }
