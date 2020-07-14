'''

violaslayer config
'''

#traceback_limit = 4
#
##btc connect 
#btc_conn = {'rpcuser':'btc', 'rpcpassword':'btc', 'rpcip':'127.0.0.1', 'rpcport':18332}
#
##db info type(bfilter)
#db_list=[
#        #remote
#        {'host':['127.0.0.1:37017'], 'db':'base','user':'violas', 'password':'violas@palliums', 'authdb' : 'admin', 'rsname':'rsviolas'},
#        {'host':['127.0.0.1:37017'], 'db':'b2vproof','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
#        {'host':['127.0.0.1:37017'], 'db':'markproof','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
#        {'host':['127.0.0.1:37017'], 'db':'addresses','user':'violas', 'password':'violas@palliums', 'authdb':'admin', 'rsname':'rsviolas'},
#        ]
#
#looping_sleep={
#        'bfilter' : 1,
#        'b2vproof' : 1,
#        'comm': 80,          #communication thread loop time
#        }
#
from tomlbase import tomlbase


class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

    def get(self, key):
        return self.content[key]

    @property
    def looping_sleep(self):
        return self.get("looping_sleep")

    @property
    def db_list(self):
        return self.get("db_list")

    @property
    def btc_conn(self):
        return self.get("btc_conn")

    @property
    def traceback_limit(self):
        return self.get("traceback_limit")

setting = tomlopt("violaslayer.toml")

