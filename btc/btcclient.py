#!/usr/bin/python3
import operator
import sys, os
import json, decimal
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
from comm.functions import json_reset
from comm.functions import json_print
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from baseobject import baseobject
from enum import Enum

#module name
name="bclient"

#btc_url = "http://%s:%s@%s:%i"

COINS = comm.values.COINS
class btcclient(baseobject):
    class transaction(object):
        def __init__(self, datas):
            self.__datas = dict(datas)
        def get_version(self):
            return self.__datas.get("version")
        def to_json(self):
            return self.__datas

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

    #height : 1612035
    #blockhash:0000000000000023d5e211d6681218cfbd39c97dc3bf21dd1b1d226d4af23688
    #txid: 9c3fdd8a5f9dff6fbd2c825650559d6180ee8eaf1938632e370d36f789984a35
    def getblockhash(self, index):
        try:
            self._logger.debug(f"start getblockhash({index})")
            if index < 0:
                ret = result(error.ARG_INVALID, f"index must be greater than or equal to 0, not {index}")
                self._logger.error(ret.message)
                return ret
            
            datas = self.__rpc_connection.getblockhash(index)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblockwithhash(self, blockhash):
        try:
            self._logger.debug(f"start getblockwithhash({blockhash})")
            if len(blockhash) != 64:
                ret = result(error.ARG_INVALID, f"blockhash must be of length 64 (not {len(blockhash)}, for '{blockhash}')")
                self._logger.error(ret.message)
                return ret
            
            datas = self.__rpc_connection.getblock(blockhash)

            ret = result(error.SUCCEED, "", json_reset(datas))
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblockwithindex(self, index):
        try:
            self._logger.debug(f"start getblockwithindex({index})")
            
            ret = self.getblockhash(index)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.getblockwithhash(ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblocktxidswithhash(self, blockhash):
        try:
            self._logger.debug(f"start getblocktxidswithhash({blockhash})")
            
            ret = self.getblockwithhash(blockhash)
            if ret.state != error.SUCCEED:
                return ret

            txs = ret.datas.get("tx")

            ret = result(error.SUCCEED, "", txs)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getblocktxidswithindex(self, index):
        try:
            self._logger.debug(f"start getblocktxidswithindex({index})")
            
            ret = self.getblockwithindex(index)
            if ret.state != error.SUCCEED:
                return ret

            txs = ret.datas.get("tx")

            ret = result(error.SUCCEED, "", txs)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getrawtransaction(self, txid, verbose = True, blockhash = None):
        try:
            self._logger.debug(f"start getrawtransaction({txid}, {verbose}, {blockhash})")
            
            if blockhash is None:
                datas = self.__rpc_connection.getrawtransaction(txid, verbose)
            else:
                datas = self.__rpc_connection.getrawtransaction(txid, verbose, blockhash)
            ret = result(error.SUCCEED, "", json_reset(datas))
            self._logger.info(f"result: {len(json_reset(ret.datas))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxoutin(self, txid):
        try:
            self._logger.debug(f"start gettxoutin({txid})")
            ret = self.getrawtransaction(txid)
            if ret.state != error.SUCCEED:
                return ret
            tran = ret.datas
            datas = {
                    "txid" : txid,
                    "vin" : [{"txid": vin.get("txid"), "vout" : vin.get("vout"), "coinbase": vin.get("coinbase"), "sequence": vin.get("sequence")} for vin in tran.get("vin")],
                    "vout" : tran.get("vout")
                    }

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))} , vout count: {len(ret.datas.get('vout'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxoutinfromdata(self, tran):
        try:
            self._logger.debug(f"start gettxoutinfromdata({tran.get('txid')})")
            datas = {
                    "txid" : tran.get("txid"),
                    "vin" : [{"txid": vin.get("txid"), "vout" : vin.get("vout"),"coinbase":vin.get("coinbase"), "sequence": vin.get("sequence")} for vin in tran.get("vin")],
                    "vout" : tran.get("vout")
                    }

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))} , vout count: {len(ret.datas.get('vout'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxin(self, txid):
        try:
            self._logger.debug(f"start gettxoutin({txid})")
            ret = self.getrawtransaction(txid)
            if ret.state != error.SUCCEED:
                return ret
            tran = ret.datas
            datas = {
                    "txid" : txid,
                    "vin" : [{"txid": vin.get("txid"), "vout" : vin.get("vout"),"coinbase":vin.get("coinbase"), "sequence": vin.get("sequence")} for vin in tran.get("vin")],
                    }

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxinfromdata(self, tran):
        try:
            self._logger.debug(f"start gettxoutin({txid})")
            datas = {
                    "txid" : tran.get("txid"),
                    "vin" : [{"txid": vin.get("txid"), "vout" : vin.get("vout"), "coinbase":vin.get("coinbase") ,"sequence": vin.get("sequence")} for vin in tran.get("vin")],
                    }

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxoutwithn(self, txid, n):
        try:
            ret = self.gettxoutin(txid)
            if ret.state != error.SUCCEED:
                return ret

            vouts = ret.datas.get("vout")
            datas = None
            for vout in vouts:
                if vout.get("n") == n:
                    ret = self.parsevout(vout)
                    return ret

            #not found txid vout n
            ret = result(error.ARG_INVALID)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxoutwithnfromdata(self, tran, n):
        try:
            vouts = tran.get("vout")
            datas = None
            for vout in vouts:
                if vout.get("n") == n:
                    ret = self.parsevout(vout)
                    return ret

            #not found txid vout n
            ret = result(error.ARG_INVALID)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parsevout(self, vout):
        try:
            datas = {}
            datas["value"] = vout.get("value", 0.0)
            datas["n"] = vout.get("n")
            scripti_pub_key = vout.get("scriptPubKey")
            if scripti_pub_key is not None:
                datas["type"] = scripti_pub_key.get("type")
                datas["asm"] = scripti_pub_key.get("asm")
                datas["hex"] = scripti_pub_key.get("hex")
                #if datas["type"] != "scripthash":
                datas["addresses"] = scripti_pub_key.get("addresses")

            ret = result(error.SUCCEED, "", datas)
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
