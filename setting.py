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
        {'host':'18.136.139.151', 'port':27017, 'db':'trans', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
        {'host':'18.136.139.151', 'port':27017, 'db':'proof', 'password':'af955c1d62a74a7543235dbb7fa46ed98948d2041dff67dfdb636a54e84f91fb', 'step':300},
        #{'host':'127.0.0.1', 'port':6378, 'db':'record', 'password':'violas', 'step':100},
        ]

looping_sleep={
        'bfilter' : 1,
        'comm': 8,          #communication thread loop time
        }
