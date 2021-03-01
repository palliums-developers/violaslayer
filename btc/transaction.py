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
#from .models import BtcRpc
from baseobject import baseobject
from enum import Enum
from btc.payload import payload

#module name
name="transaction"

#btc_url = "http://%s:%s@%s:%i"

COINS = comm.values.COINS
class transaction(baseobject):
    def __init__(self, name):
        baseobject.__init__(self, name)
        self.reset()
    
    def reset(self):
        self.inputs = None
        self.outputs = None
        self._inputsamount = 0

    @property
    def inputs(self):
        return self.__inputs

    @inputs.setter
    def inputs(self, value):
        self.__inputs = value

    @property
    def outputs(self):
        return self.__outputs

    @outputs.setter
    def outputs(self, value):
        self.__outputs = value

    @property
    def inputsamount(self):
        return self._inputsamount

    def createrawinputs(self):
        try:
            self._logger.debug(f"start createrawinputs()")
            ret = result(error.SUCCEED, "", datas=[])
        except Exception as e:
            ret = parse_except(e)
        return ret

    def cleaninputs(self):
        self._inputsamount = 0
        self.inputs = self.createrawinputs().datas

    def cleanoutputs(self):
        self.outputs = self.createrawoutputs().datas

    def appendinput(self, txid, n, amount = None, sequence = None):
        try:
            if self.inputs is None:
                self.inputs = self.createrawinputs().datas
            input = {"txid": txid, "vout": n}
            if sequence is not None:
                input["sequence"] = sequence

            if amount is not None:
                self._inputsamount += amount

            self.inputs.append(input)

            ret = result(error.SUCCEED, "", self.inputs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def createrawoutputs(self):
        try:
            self._logger.debug(f"start createrawoutputs()")
            ret = result(error.SUCCEED, "", datas=[])
        except Exception as e:
            ret = parse_except(e)
        return ret

    def appendoutput(self, address, amount): #amount is float BTC
        try:
            if address is None:
                return result(error.ARG_INVALID)

            if self.outputs is None:
                self.outputs = self.createrawoutputs().datas
            output = {address:round(amount, 8)}

            self.outputs.append(output)

            ret = result(error.SUCCEED, "", self.outputs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def updateoutput(self, address, amount): #amount is float BTC
        try:
            if self.outputs is None:
                self.outputs = self.createrawoutputs().datas
            
            update = {address:round(amount, 8)}
            for output in self.outputs:
                if address in output.keys():
                    output.update(update)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def getoutputamount(self): #amount is float BTC
        try:
            amount_sum = 0.0
            if self.outputs is not None:
                for output in self.outputs:
                    if output.get("data") is not None:
                        continue
                    print(output.values())
                    amount_sum += sum(output.values())
            ret = result(error.SUCCEED, "", amount_sum)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def appendoutputdata(self, data): 
        try:
            if self.outputs is None:
                self.outputs = self.createrawoutputs().datas
            output = {"data": data}

            self.outputs.append(output)

            ret = result(error.SUCCEED, "", self.outputs)
        except Exception as e:
            ret = parse_except(e)
        return ret

