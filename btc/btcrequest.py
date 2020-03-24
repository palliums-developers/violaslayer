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

    def __listexproofforstate(self, state, extype, receiver, excluded):
        try:
            self._logger.debug(f"start __listexproofforstate(state={state} type={extype} receiver={receiver} excluded={excluded})")
            if(len(receiver) == 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
            
            if excluded is None or len(excluded) == 0:
                datas = self.__rpc_connection.violas_listexproofforstate(state, extype, receiver)
            else:
                datas = self.__rpc_connection.violas_listexproofforstate(state, extype, receiver, excluded)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def stop(self):
        self.work_stop()

    def __listexproof(self, extype, cursor = 0, limit = 10):
        try:
            self._logger.debug(f"start __listexproof(type={extype} cursor={cursor} limit={limit})")
            
            datas = self.__rpc_connection.violas_listexproof(extype, cursor, limit)

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def isexproofcomplete(self, address, sequence):
        try:
            self._logger.debug(f"start isexproofcomplete(address = {address} sequence={sequence})")
            if(len(address) != 64 or sequence < 0):
                return result(error.ARG_INVALID, error.argument_invalid, "")
                
            datas = self.__rpc_connection.violas_isexproofcomplete(address, sequence)
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def listexproofforstart(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.START.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofforend(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.END.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofforcancel(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.CANCEL.value, comm.values.EX_TYPE_B2V, receiver, excluded)

    def listexproofformark(self, receiver, excluded):
        return self.__listexproofforstate(self.proofstate.MARK.value, comm.values.EX_TYPE_V2B, receiver, excluded)

    def listexproofforb2v(self, cursor, limit):
        return self.__listexproof(comm.values.EX_TYPE_B2V, cursor, limit)

    def __map_tran(self, data):
        tran_data = json.dumps({"flag":"btc", "type":"b2v", "state":data.get("state"), "to_address":data.get("address"), "to_module":data.get("vtoken"), "tran_id":data.get("txid")})
        return {
                "version": data.get("index"),\
                "success":True,\
                "events":[{"event":tran_data}],\
                "data":tran_data,\
                "amount":int(data.get("amount") * COINS),\
                "sequence_number":data.get("height"),\
                "txid":data.get("txid"),\
                "tran_id":data.get("txid"),\
                "creation_block":data.get("creation_block"),\
                "update_block":data.get("update_block"),\
                "sender":data.get("issuer"), \
                "receiver":data.get("receiver"),\
                "module_address":data.get("vtoken")
                }

    def get_transactions(self, cursor, limit, nouse=True):
        try:
            ret = self.listexproofforb2v(cursor, limit)
            if ret.state != error.SUCCEED:
                return ret
            datas = []
            for data in ret.datas:
                tran = self.__map_tran(data)
                datas.append(self.transaction(tran))
            ret = result(error.SUCCEED, "", datas)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            latest_index = self.__rpc_connection.violas_getexprooflatestindex(comm.values.EX_TYPE_B2V)
            ret = result(error.SUCCEED, "", latest_index.get("index", -1))
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendexproofstart(self, fromaddress, toaddress, amount, vaddress, sequence, vtoken):
        try:
            self._logger.info(f"start sendexproofstart (fromaddress={fromaddress}, toaddress={toaddress}, amount={amount:.8f}, vaddress={vaddress}, sequence={sequence}, vtoken={vtoken})")
            if(len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 \
                    or sequence < 0 or len(vtoken) != 64):
                return result(error.ARG_INVALID, "len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 or sequence < 0 or len(vtoken) !=64", "")
            datas = self.__rpc_connection.violas_sendexproofstart(fromaddress, toaddress, f"{amount:.8f}", vaddress, sequence, vtoken)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendexproofend(self, fromaddress, toaddress, vaddress, sequence, amount, version):
        try:
            self._logger.info(f"start sendexproofend (fromaddress={fromaddress}, toaddress={toaddress}, vaddress={vaddress}, sequence={sequence}, amount={amount:.8f}, version={version})")
            if(len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) != 64 
                    or sequence < 0 or version< 0):
                return result(error.ARG_INVALID, "len(fromaddress) == 0 or len(toaddress) == 0 or fromaddress == toaddress or len(vaddress) == 0 or sequence < 0 or version < 0", "")
            datas = self.__rpc_connection.violas_sendexproofend(fromaddress, toaddress, vaddress, sequence, f"{amount:.8f}", version)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendtoaddress(self, address, amount):
        try:
            self._logger.info(f"start sendtoaddress(address={address}, amount={amount})")
            datas = self.__rpc_connection.sendtoaddress(address, f"{amount:.8f}")
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret
   
    def sendexproofmark(self, fromaddress, toaddress, toamount, vaddress, sequence, version):
        try:
            self._logger.info(f"start sendexproofmark(fromaddress={fromaddress}, toaddress={toaddress}, toamount={toamount:.8f}, vaddress={vaddress}, sequence={sequence}, version={version})")
            datas = self.__rpc_connection.violas_sendexproofmark(fromaddress, toaddress, f"{toamount:.8f}", vaddress, sequence, version)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def generatetoaddress(self, count, address):
        try:
            self._logger.info(f"start generatetoaddress(count={count}, address={address})")
            datas = self.__rpc_connection.generatetoaddress(count, address)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def listunspent(self, minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
        try:
            self._logger.debug(f"start listunspent(minconf={minconf}, maxconf={maxconf}, addresses={addresses}, include_unsafe={include_unsafe}, query_options={query_options})")
            datas = self.__rpc_connection.listunspent(minconf, maxconf, addresses, include_unsafe, query_options)
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

    def getwalletbalance(self):
        try:
            self._logger.debug("start getwalletbalance")
            walletinfo = self.__rpc_connection.getwalletinfo()
            balance = walletinfo.get("balance", 0)
            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas:.8f}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getwalletaddressbalance(self, address):
        try:
            self._logger.debug(f"start getwalletaddressbalance({address})")
            addresses = [address]
            datas = self.__rpc_connection.listunspent(1, 999999999, addresses)
            balance = 0
            if len(datas) == 0:
                return result(error.FAILED)
            for data in datas:
                balance += data.get("amount", 0)

            ret = result(error.SUCCEED, "", balance)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_btc_banlance(self, address, vamount, gas = comm.values.MIN_EST_GAS):
        try:
            self._logger.debug(f"start has_btc_banlance(address={address}, vamount={vamount}, gas={gas})")
            ret = self.getwalletaddressbalance(address)
            if ret.state != error.SUCCEED:
                return ret
    
            #change bitcoin unit to satoshi and check amount is sufficient
            wbalance = int(ret.datas * comm.values.COINS)
            if wbalance <= (vamount + gas): #need some gas, so wbalance > vamount
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_v2b_mark(self, address, version):
        try:
            self._logger.debug(f"start has_v2b_mark(address = {address}, version={version})")
            datas = self.__rpc_connection.violas_getexproofforaddress(address, version, comm.values.EX_TYPE_V2B)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_b2v_mark(self, address, version):
        try:
            self._logger.debug(f"start has_b2v_mark(address = {address}, version={version})")
            datas = self.__rpc_connection.violas_getexproofforaddress(address, version, comm.values.EX_TYPE_B2V)
            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: {ret.datas}")
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
