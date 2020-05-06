#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import hashlib
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
from btc.btcclient import btcclient
from enum import Enum
from db.dbvfilter import dbvfilter
from baseobject import baseobject
from btc.payload import payload

#module name
name="abase"

COINS = comm.values.COINS
class abase(baseobject):
    #enum name must be transaction datas "type"
    #collect list
    ##  blockinfo     -block info       key = blockhash  ;  key = height
    ##  transaction   -rawtransaction   key = txid
    ##  txout         -transaction      key = txid + n
    ##  wallet        -addresses txout  key = address
    ##  exproof       -btc violas map   key = index (0~n)

    class txoutstate(Enum):
        NOUSE       = 1
        USED        = 2

    class collection(Enum):
        BLOCKINFO   = 1
        TRANSACTION = 2
        TXOUT       = 3
        WALLET      = 4
        EXPROOF     = 5
        OPTRANSACTION = 6

    def __init__(self, name, dbconf, vnodes):
        baseobject.__init__(self, name)
        self._step = 0
        self._min_valid_version = -1
        self._dbclient = None
        self._vclient = None
        self._connect_db(name, dbconf)
        self._connect_btc(name, vnodes)
        pass

    def __del__(self):
        if self._dbclient is not None:
            pass

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host", "127.0.0.1:37017"), rconf.get("db"), rconf.get("user", None), rconf.get("password", None), rconf.get("authdb", "admin"), newdb = rconf.get("newdb", True), rsname=rconf.get("rsname", None))
        return self._dbclient

    def _connect_btc(self, name, node):
        if node is not None:
            self._vclient = btcclient(name, node) 
        return self._vclient

    def set_min_valid_version(self, version):
        self._min_valid_version = version
        self._logger.debug(f"set min valid version {self.get_min_valid_version()}")

    def get_min_valid_version(self):
        self._logger.debug(f"get min valid version {self._min_valid_version}")
        return self._min_valid_version

    def get_start_version(self, version):
        return int(max(self.get_min_valid_version(), version))

    def stop(self):
        if self._vclient is not None:
            self._vclient.stop()
        self.work_stop()

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def create_tran_id(self, address, sequence):
        return f"{txid}_{sequence}"

    def json_to_dict(self, data):
        try:
            data = json.loads(data)
            ret = result(error.SUCCEED, "", data)
        except Exception as e:
            ret = result(error.FAILED, "data is not json format.")
        return ret

    def parse_txin(self, tran):
        try:
            ret = self._vclient.gettxinwithnfromdata(tran, 0)
            if ret.state != error.SUCCEED:
                return ret
            vin = ret.datas

            txid = vin.get("txid")
            vout = vin.get("vout")

            ret = self.get_transaction(txid)
            if ret.state != error.SUCCEED:
                return ret
            pre_tran = ret.datas
            ret = self._vclient.gettxoutwithnfromdata(pre_tran, vout)
            if ret.state != error.SUCCEED:
                return ret
            
            input_type = ret.datas.get("type")

            if not self.is_allow_inputtype(input_type):
                return result(error.ARG_INVALID, "input type is invalid.")

            datas = {
                    "address": ret.datas.get("addresses")[0]
                    }
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parse_tran(self, tran):
        try:
            ret = self.parse_txin(tran)
            if ret.state != error.SUCCEED:
                return ret

            receiver = None
            amount = 0
            payload_hex = None
            issuser = ret.datas.get("address")
            vout_count = self._vclient.gettxoutcountfromdata(tran)
            if vout_count < 2:
                return result(error.TRAN_INFO_INVALID)
            elif vout_count == 2:
                for i in range(i):
                    ret = self._vclient.gettxoutwithnfromdata(tran, i)
                    if ret.state != error.SUCCEED:
                        return ret

                    vout = ret.datas
                    if self.is_opreturn(vout.get("type")):
                        payload_hex = vout.get("hex")
                        continue
                    
                    receiver = vout.get("addresses")[0]
                    amount = vout.get("value")
            else:
                for i in range(i):
                    ret = self._vclient.gettxoutwithnfromdata(tran, i)
                    if ret.state != error.SUCCEED:
                        return ret

                    vout = ret.datas
                    if self.is_opreturn(vout.get("type")):
                        payload_hex = vout.get("hex")
                        continue

                    address = vout.get("addresses")[0]
                    if issuser == address:
                        continue
                    amount = vout.get("value")
                    receiver = address

            if receiver is None or payload_hex is None:
                return result(error.TRAN_INFO_INVALID)

            payload_parse = payload(self.name())
            ret = payload_parse.parse(payload_hex)
            if ret.state != error.SUCCEED:
                return ret

            payload_info = ret.datas

            datas = {\
                    "create_block": tran.get("blockhash"), 
                    "update_block": tran.get("blockhash"),
                    "address":payload_info.proof_data.get("to_address"),
                    "vtoken":payload_info.proof_data.get("token"), #token is module
                    "num_btc":amount,
                    "issuer":issuser, 
                    "receiver":receiver, 
                    "sequence":payload_info.proof_data.get("sequence"),
                    "state":payload_info.tx_type,
                    "type":payload_info.proof_type,
                    }
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

    def get_transaction(self, txid):
        try:
            ret = self._vclient.getrawtransaction(txid)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_txout_id(self, txid, n):
        return f"{txid}_{n}"

    def is_allow_inputtype(self, scrpittype):
        #nonstandard  pubkey pubkeyhash scripthash multisig nulldata witness_v0_keyhash witness_v0_scripthash witness_unknown
        return scrpittype in ["scripthash", "witness_v0_keyhash", "witness_v0_scripthash", "pubkeyhash"]

    def is_allow_outputtype(self, scrpittype):
        #nonstandard  pubkey pubkeyhash scripthash multisig nulldata witness_v0_keyhash witness_v0_scripthash witness_unknown
        return scrpittype in ["scripthash", "witness_v0_keyhash", "witness_v0_scripthash", "pubkeyhash", "nulldata"]
        
    def is_opreturn(self, scrpittype):
        #nonstandard  pubkey pubkeyhash scripthash multisig nulldata witness_v0_keyhash witness_v0_scripthash witness_unknown
        return scrpittype in ["nulldata"]
        
