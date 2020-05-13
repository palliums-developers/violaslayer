#!/usr/bin/python3
import operator
import sys, os
import json, decimal
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import log
import log.logger
import traceback
import datetime
import stmanage
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
from btc.payload import payload
from btc.transaction import transaction

#module name
name="bclient"

#btc_url = "http://%s:%s@%s:%i"

COINS = comm.values.COINS
class btcclient(baseobject):

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

    def getaddressunspent(self, address, minconf = 0, maxconf = 99999999):
        try:
            self._logger.debug(f"start getaddressunspent(address={address}, minconf = {minconf}, maxconf={maxconf})")
            datas = self.__rpc_connection.listunspent(minconf, maxconf, [address])
            unspent = {}
            filter = []
            amount_sum = 0
            for data in datas:
                amount_sum += int(data.get("amount") * COINS)
                filter.append({"txid": data.get("txid"), \
                        "amount": int(data.get("amount") * COINS), \
                        "vout":data.get("vout")})

            unspent = {"amountsum": amount_sum, "unspents": filter}
            ret = result(error.SUCCEED, "", unspent)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def getamountlist(self, amount, amounts):
        amounts.sort()
        use_amounts = None
        if amounts is None or len(amounts) == 0:
            return None

        if amount > sum(amounts):
            print(f"amounts sum({sum(amounts)}) is too small. amount : {amount}")
            return None

        if amount <= amounts[0]:
            use_amounts = [amounts[0]]
        elif amount >= amounts[len(amounts) - 1]:
            use_amounts = [amounts[len(amounts) -1]]
            new_amount = amount - amounts[len(amounts) -1]
            amounts.pop()
            if new_amount > 0:
                ret = self.getamountlist(new_amount, amounts)
                if ret is not None:
                    use_amounts.extend(ret)
        else:
            #get split idx
            idx_split = -1
            for idx, av in enumerate(amounts):
                idx_split = idx  #index : av > amount
                if av > amount:
                    break
            start_idx = 0;
            if idx_split > 3:
                start_idx = idx_split - 3

            sub_sum = sum(amounts[start_idx:idx_split])
            if amount <= sub_sum :
                idx_split = idx_split - 1
            use_amounts = [amounts[idx_split]]

            new_amount = amount - sum(use_amounts)
            if new_amount > 0:
                amounts.pop(idx_split)
                ret = self.getamountlist(new_amount, amounts)
                if ret is not None:
                    use_amounts.extend(ret)

        return use_amounts

    def getaddressunspentwithamount(self, address, amount, minconf = 0, maxconf = 99999999):
        try:
            self._logger.debug(f"start getaddressunspent(address={address}, minconf = {minconf}, maxconf={maxconf})")
            ret = self.getaddressunspent(address, minconf, maxconf)
            if ret.state != error.SUCCEED:
                return ret

            if ret.datas.get("amountsum") < amount:
                return result(error.ARG_INVALID, "address amount({ret.datas.get('amountsum')}) too small. ")

            unspents = ret.datas.get("unspents")
            print(unspents)
            amounts = [v.get("amount") for v in unspents]
            print(amounts)
            use_amounts = self.getamountlist(amount, list(amounts))

            datas = []
            for unspent in unspents:
                if unspent.get("amount") in use_amounts:
                    datas.append(unspent)
                    use_amounts.remove(unspent.get("amount"))

            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def createrawtransaction(self, inputs, outputs, locktime = 0, replaceable = False):
        try:
            self._logger.debug(f"start createrawtransaction(inputs={inputs}, outputs = {outputs}, locktime={locktime}, replaceable={replaceable})")
            datas = self.__rpc_connection.createrawtransaction(inputs, outputs, locktime, replaceable)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def signrawtransactionwithkey(self, hexstring, privkeys, prevtxs=None, sighashtype="ALL"):
        try:
            self._logger.debug(f"start signrawtransactionwithkey(hexstring=hexstring, privkeys= {privkeys}, sighashtype={sighashtype})")
            datas = self.__rpc_connection.signrawtransactionwithkey(hexstring, privkeys)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def estimatesmartfee(self, target, mode="CONSERVATIVE"):
        try:
            self._logger.debug(f"estimatesmartfee(target={target}, mode={mode})")
            datas = self.__rpc_connection.estimatesmartfee(target, mode)
            if datas.get("errors") is not None:
                ret = result(error.FAILED, datas.get("errors"))

            ret = result(error.SUCCEED, "", float(datas.get("feerate")))
        except Exception as e:
            ret = parse_except(e)
        return ret

    @property
    def satoshiperk(self):
        return self.__satoshi_per_k

    def getminfeerate(self, satoshiperk, size):
        try:
            self._logger.debug(f"start getminfeerate(satoshiperk={satoshiperk}, size={size})")
            datas = satoshiperk * size / 1000.0
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sendrawtransaction(self, hexstring, maxfeerate=0.010):
        try:
            self._logger.debug(f"start sendrawtransaction(hexstring={hexstring}, maxfeerate={maxfeerate})")
            datas = self.__rpc_connection.sendrawtransaction(hexstring, maxfeerate)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

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
            self._logger.info(f"result: {len(ret.datas.get('tx'))}")
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
            datas["vinsize"] = len(datas.get("vin"))
            datas["voutsize"] = len(datas.get("vout"))
            datas["txid"] = txid 
            for i, value in enumerate(datas["vout"]):
                script_pub_key = datas["vout"][i]["scriptPubKey"]
                if script_pub_key.get("type", "") == "nonstandard":
                    script_pub_key["asm"] = ""
                    script_pub_key["hex"] = ""

            ret = result(error.SUCCEED, "", json_reset(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    
    def decoderawtransaction(self, data, isswitness = True):
        try:
            self._logger.debug(f"start decoderawtransaction({data}, {isswitness})")
            
            datas = self.__rpc_connection.decoderawtransaction(data, isswitness)
            datas["vinsize"] = len(datas.get("vin"))
            datas["voutsize"] = len(datas.get("vout"))
            datas["weight"] = datas.get("weight")
            for i, value in enumerate(datas["vout"]):
                script_pub_key = datas["vout"][i]["scriptPubKey"]
                if script_pub_key.get("type", "") == "nonstandard":
                    script_pub_key["asm"] = ""
                    script_pub_key["hex"] = ""

            ret = result(error.SUCCEED, "", json_reset(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret
    # get vout vin
    def gettxoutin(self, txid):
        try:
            self._logger.debug(f"start gettxoutin({txid})")
            ret = self.getrawtransaction(txid)
            if ret.state != error.SUCCEED:
                return ret
            tran = ret.datas

            ret = self.gettxinfromdata(tran)
            if ret.state != error.SUCCEED:
                return ret

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
                    "vin" : [{"txid": vin.get("txid"), \
                            "vout" : vin.get("vout"),\
                            "coinbase":vin.get("coinbase"), \
                            "sequence": vin.get("sequence")} \
                            for vin in tran.get("vin")],
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

            datas = self.gettxinfromdata(tran)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxinfromdata(self, tran):
        try:
            self._logger.debug(f"start gettxoutinfromdata({tran.get('txid')})")
            datas = {
                    "txid" : tran.get("txid"),
                    "vin" : [{"txid": vin.get("txid"), \
                            "vout" : vin.get("vout"), \
                            "coinbase":vin.get("coinbase") ,\
                            "sequence": vin.get("sequence")} \
                            for vin in tran.get("vin")],
                    }

            ret = result(error.SUCCEED, "", datas)
            self._logger.info(f"result: vin count: {len(ret.datas.get('vin'))}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxinwithnfromdata(self, tran, n):
        try:
            self._logger.debug(f"start gettxinwithnfromdata(tran, {n})")
            ret = self.gettxinfromdata(tran)
            if ret.state != error.SUCCEED:
                return ret

            vins = ret.datas.get("vin")
            datas = None
            for index, vin in enumerate(vins):
                if index == n:
                    return result(error.SUCCEED, "", vin)

            #not found txid vout n
            ret = result(error.ARG_INVALID, f"not found index({n}) in tx vins. transaction:{tran}")
        except Exception as e:
            ret = parse_except(e)
        return ret
    def gettxoutwithn(self, txid, n):
        try:
            self._logger.debug(f"start gettxoutwithn({txid}, {n})")
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
            ret = result(error.ARG_INVALID, f"not found index({n}) in tx vouts")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def gettxoutcountfromdata(self, tran):
        try:
            vouts = tran.get("vout")
            #not found txid vout n
            ret = result(error.SUCCEED, datas = len(vouts))
        except Exception as e:
            ret = parse_except(e)
        return ret
    def gettxoutwithnfromdata(self, tran, n):
        try:
            self._logger.debug(f"start gettxoutwithnfromdata(tran, {n})")
            vouts = tran.get("vout")
            datas = None
            for vout in vouts:
                if vout.get("n") == n:
                    ret = self.parsevout(vout)
                    return ret

            #not found txid vout n
            ret = result(error.ARG_INVALID, f"not found index({n}) in tx vouts")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getopreturnfromdata(self, tran):
        try:
            self._logger.debug(f"start getopreturnfromdata(tran)")
            vouts = tran.get("vout")
            datas = None
            for vout in vouts:
                ret = self.parsevout(vout)
                if ret.state != error.SUCCEED:
                    return ret
                if ret.datas.get("type") == "nulldata":
                    return result(error.SUCCEED, "", ret.datas.get("hex"))

            #not found txid vout n
            ret = result(error.ARG_INVALID, f"not found txout type is nulldata")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parsevout(self, vout):
        try:
            datas = {}
            datas["value"] = vout.get("value", 0.0)
            datas["n"] = vout.get("n")
            script_pub_key = vout.get("scriptPubKey")
            if script_pub_key is not None:
                datas["type"] = script_pub_key.get("type")
                datas["asm"] = script_pub_key.get("asm")
                datas["hex"] = script_pub_key.get("hex")
                #if datas["type"] != "scripthash":
                datas["addresses"] = script_pub_key.get("addresses")

            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e, "parsevount Exception")
        return ret

    def parsevin(self, vin):
        try:
            datas = {}
            datas["vout"] = vin.get("vout")
            datas["txid"] = vin.get("txid")
            datas["sequence"] = vin.get("sequence")

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
def test_createrawtransaction():
        receiver_addr = "2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien"
        combin_addr = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB"
        sender_addr = "2MxBZG7295wfsXaUj69quf8vucFzwG35UWh" 
        pl = payload(name)
        toaddress = "dcfa787ecb304c20ff24ed6b5519c2e5cae5f8464c564aabb684ecbcc19153e9"
        sequence = 20200512001
        module = "00000000000000000000000000000000e1be1ab8360a35a0259f1c93e3eac736"
        print(f'''************************************************************************create ex start
        toaddress:{toaddress}
        sequence: {sequence}
        module:{module}
**********************************************************************************''')
        ret = pl.create_ex_start(toaddress, sequence, module)
        assert ret.state == error.SUCCEED, f"payload create_ex_start.{ret.message}"
        data = ret.datas

        client = btcclient(name, stmanage.get_btc_conn())
        tran = transaction(name)
        tran.appendoutput(receiver_addr, 0.000001)
        tran.appendoutput(combin_addr, 0.000002)
        tran.appendoutputdata(data)
        
        ret = tran.getoutputamount()
        print("output amount sum: {ret.datas * COINS}")

        ret = client.getaddressunspentwithamount(sender_addr, ret.datas * COINS)
        unspents = ret.datas
        for unspent in unspents:
            tran.appendinput(unspent.get("txid"), unspent.get("vout"))

        print(f"inputs: {tran.inputs}")
        print(f"outputs: {tran.outputs}")
        ret = client.createrawtransaction(tran.inputs, tran.outputs)
        assert ret.state == error.SUCCEED, ret.message

        privkeys = ["cUrpMtcfh4s9CRdPEA2tx3hYQGb5yy7pkWQNzaMBZc8Sj42g8YA8"]
        ret = client.signrawtransactionwithkey(ret.datas, privkeys)
        assert ret.state == error.SUCCEED, ret.message
        tran = ret.datas
        print("*"*30)
        json_print(tran)

        estimatefee = client.estimatesmartfee(6).datas
        print(f"estimatefee:{estimatefee}")

        ret = client.decoderawtransaction(tran.get("hex"))
        weight = ret.datas.get("weight")
        ret = client.getminfeerate(estimatefee, weight)
        print(f"transaction minfeerate:{ret.datas:.8f}")


def main():
    try:
        amounts = [1, 2, 3, 5, 8, 13, 21, 34, 36, 40, 50, 52, 100, 200]
        ret = btcclient.getamountlist(int(sys.argv[1]), list(amounts))
        print(f"list:{amounts}")
        print(f"use amount: {ret}")

    except Exception as e:
        parse_except(e)
    finally:
        print("end main")

if __name__ == "__main__":
    #main()
    test_createrawtransaction()

