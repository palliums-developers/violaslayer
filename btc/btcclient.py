#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbb2v import dbb2v
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from baseobject import baseobject
from enum import Enum

#module name
name="bclient"

#btc_url = "http://%s:%s@%s:%i"

COINS = int(comm.values.COINS * (100000000/comm.values.COINS))
class btcclient(baseobject):

    class transaction(object):
        def __init__(self, datas):
            self.__datas = dict(datas)
        def get_version(self):
            return self.__datas.get("version")
        def to_json(self):
            return self.__datas

    class proofstate(Enum):
        START   = "start"
        END     = "end"
        CANCEL  = "cancel"
        MARK    = "mark"

    def __init__(self, name, btc_conn):
        self.__btc_url               = "http://%s:%s@%s:%i"
        self.__rpcuser               = "btc"
        self.__rpcpassword           = "btc"
        self.__rpcip                 = "127.0.0.1"
        self.__rpcport               = 9409
        self.__rpc_connection        = ""
        baseobject.__init__(self, name)

        if btc_conn :
            if btc_conn["rpcuser"]:
                self.__rpcuser = btc_conn["rpcuser"]
            if btc_conn["rpcpassword"]:
                self.__rpcpassword = btc_conn["rpcpassword"]
            if btc_conn["rpcip"]:
                self.__rpcip = btc_conn["rpcip"]
            if btc_conn["rpcport"]:
                self.__rpcport = btc_conn["rpcport"]
        self._logger.debug("connect btc server(rpcuser={}, rpcpassword={}, rpcip={}, rpcport={})".format(btc_conn["rpcuser"], btc_conn["rpcpassword"], btc_conn["rpcip"], btc_conn["rpcport"]))
        self.__rpc_connection = AuthServiceProxy(self.__btc_url%(self.__rpcuser, self.__rpcpassword, self.__rpcip, self.__rpcport))
        self._logger.debug(f"connection succeed.")

    def disconn_node(self):
        pass


    def stop(self):
        self.work_stop()

    def getblockcount(self):
        try:
            self._logger.debug(f"start getblockcount()")
            
            datas = self.__rpc_connection.getblockcount()

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    #height : 1665928
    #blockhash:000000000005004efd0671c700f220b93adaf027d7277cce47ba166d5e1a0a88
    def getblockhash(self, index):
        try:
            self._logger.debug(f"start getblockhash({index})")
            if index < 0:
                ret = result(error.ARG_INVALID, f"index must be greater than or equal to 0, not {index}")
                self._logger.error(ret.message)
                return ret
            
            datas = self.__rpc_connection.getblockhash()

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblockforhash(self, blockhash):
        try:
            self._logger.debug(f"start getblockforhash({blockhash})")
            if len(blockhash) != 64:
                ret = result(error.ARG_INVALID, f"blockhash must be of length 64 (not {len(blockhash)}, for '{blockhash}')")
                self._logger.error(ret.message)
                return ret
            
            datas = self.__rpc_connection.getblock(blockhash)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblockforindex(self. index):
        try:
            self._logger.debug(f"start getblockforindex({index})")
            
            ret = self.getblockhash(index)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.getblockforhash(ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblocktxidsforhash(self. blockhash):
        try:
            self._logger.debug(f"start getblocktxidsforhash({blockhash})")
            
            ret = self.getblockforhash(index)
            if ret.state != error.SUCCEED:
                return ret

            txs = ret.datas.get("tx")

            ret = result(error.SUCCEED, "", txs)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblocktxidsforindex(self. index):
        try:
            self._logger.debug(f"start getblocktxidsforindex({index})")
            
            ret = self.getblockforindex(index)
            if ret.state != error.SUCCEED:
                return ret

            txs = ret.datas.get("tx")

            ret = result(error.SUCCEED, "", txs)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def help(self):
        try:
            self._logger.debug("start help")
            datas = self.__rpc_connection.help()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

def main():
    try:
       #load logging
       pass

    except Exception as e:
        parse_except(e)
    finally:
        self._logger.info("end main")

if __name__ == "__main__":
    main()
