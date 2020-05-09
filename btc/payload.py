#!/usr/bin/python3
# -*- coding: utf-8 -*-

import operator
import sys, os
import json, decimal
import struct, array
import numpy as np
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
from comm.functions import json_print, json_dumps, json_reset
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from baseobject import baseobject
import btc.parse_exchange as parse_exchange
from enum import Enum

#module name
name="payload"
class payload(baseobject):
    __valid_mark = "violas"
    __version_0 = 0
    __version_1 = 1

    class optcodetype(Enum):
        # push value
        OP_0 = 0x00
        OP_FALSE = OP_0
        OP_PUSHDATA1 = 0x4c
        OP_PUSHDATA2 = 0x4d
        OP_PUSHDATA4 = 0x4e
        OP_1NEGATE = 0x4f
        OP_RESERVED = 0x50
        OP_1 = 0x51
        OP_TRUE=0x51
        OP_2 = 0x52
        OP_3 = 0x53
        OP_4 = 0x54
        OP_5 = 0x55
        OP_6 = 0x56
        OP_7 = 0x57
        OP_8 = 0x58
        OP_9 = 0x59
        OP_10 = 0x5a
        OP_11 = 0x5b
        OP_12 = 0x5c
        OP_13 = 0x5d
        OP_14 = 0x5e
        OP_15 = 0x5f
        OP_16 = 0x60

        ## control
        OP_NOP      = 0x61
        OP_VER      = 0x62
        OP_IF       = 0x63
        OP_NOTIF    = 0x64
        OP_VERIF    = 0x65
        OP_VERNOTIF = 0x66
        OP_ELSE     = 0x67
        OP_ENDIF    = 0x68
        OP_VERIFY   = 0x69
        OP_RETURN   = 0x6a
        ## stack ops
        OP_TOALTSTACK   = 0x6b
        OP_FROMALTSTACK = 0x6c
        OP_2DROP    = 0x6d
        OP_2DUP     = 0x6e
        OP_3DUP     = 0x6f
        OP_2OVER    = 0x70
        OP_2ROT     = 0x71
        OP_2SWAP    = 0x72
        OP_IFDUP    = 0x73
        OP_DEPTH    = 0x74
        OP_DROP     = 0x75
        OP_DUP      = 0x76
        OP_NIP      = 0x77
        OP_OVER     = 0x78
        OP_PICK     = 0x79
        OP_ROLL     = 0x7a
        OP_ROT      = 0x7b
        OP_SWAP     = 0x7c
        OP_TUCK     = 0x7d

        # splice ops
        OP_CAT      = 0x7e
        OP_SUBSTR   = 0x7f
        OP_LEFT     = 0x80
        OP_RIGHT    = 0x81
        OP_SIZE     = 0x82

        # bit logic
        OP_INVERT   = 0x83
        OP_AND      = 0x84
        OP_OR       = 0x85
        OP_XOR      = 0x86
        OP_EQUAL    = 0x87
        OP_EQUALVERIFY  = 0x88
        OP_RESERVED1    = 0x89
        OP_RESERVED2    = 0x8a

        # numeric
        OP_1ADD     = 0x8b
        OP_1SUB     = 0x8c
        OP_2MUL     = 0x8d
        OP_2DIV     = 0x8e
        OP_NEGATE   = 0x8f
        OP_ABS      = 0x90
        OP_NOT      = 0x91
        OP_0NOTEQUAL    = 0x92

        OP_ADD      = 0x93
        OP_SUB      = 0x94
        OP_MUL      = 0x95
        OP_DIV      = 0x96
        OP_MOD      = 0x97
        OP_LSHIFT   = 0x98
        OP_RSHIFT   = 0x99

        OP_BOOLAND  = 0x9a
        OP_BOOLOR   = 0x9b
        OP_NUMEQUAL = 0x9c
        OP_NUMEQUALVERIFY   = 0x9d
        OP_NUMNOTEQUAL      = 0x9e
        OP_LESSTHAN         = 0x9f
        OP_GREATERTHAN      = 0xa0
        OP_LESSTHANOREQUAL  = 0xa1
        OP_GREATERTHANOREQUAL = 0xa2
        OP_MIN      = 0xa3
        OP_MAX      = 0xa4

        OP_WITHIN   = 0xa5

        # crypto
        OP_RIPEMD160 = 0xa6
        OP_SHA1     = 0xa7
        OP_SHA256   = 0xa8
        OP_HASH160  = 0xa9
        OP_HASH256  = 0xaa
        OP_CODESEPARATOR = 0xab
        OP_CHECKSIG = 0xac
        OP_CHECKSIGVERIFY = 0xad
        OP_CHECKMULTISIG = 0xae
        OP_CHECKMULTISIGVERIFY = 0xaf

        # expansion
        OP_NOP1 = 0xb0
        OP_CHECKLOCKTIMEVERIFY = 0xb1
        OP_NOP2 = OP_CHECKLOCKTIMEVERIFY
        OP_CHECKSEQUENCEVERIFY = 0xb2
        OP_NOP3 = OP_CHECKSEQUENCEVERIFY
        OP_NOP4 = 0xb3
        OP_NOP5 = 0xb4
        OP_NOP6 = 0xb5
        OP_NOP7 = 0xb6
        OP_NOP8 = 0xb7
        OP_NOP9 = 0xb8
        OP_NOP10 = 0xb9
        # template matching params violas
        OP_SMALLINTEGER = 0xfa
        OP_PUBKEYS      = 0xfb
        OP_PUBKEYHASH   = 0xfd
        OP_PUBKEY       = 0xfe
        OP_INVALIDOPCODE = 0xff

    class txtype(Enum):
        BTC_MARK    = 0x1030
        EX_START    = 0x3000
        EX_END      = 0x3001
        EX_CANCEL   = 0x3002
        EX_MARK     = 0x3010
        UNKNOWN     = 0xFFFF

    def __init__(self, name):
        baseobject.__init__(self, name)
        self.bigendian_flag = self.is_bigendian()
        self._type_version = {}
        self.__init_type_with_version()
        self._reset(None)

    def __init_type_with_version(self):
        self._type_version = {
                        self.txtype.BTC_MARK : {"version" : [self.__version_1, self.__version_0], "block": 0}, \
                        self.txtype.EX_START : {"version" : [self.__version_1], "block": 0}, \
                        self.txtype.EX_END   : {"version" : [self.__version_1], "block": 0}, \
                        self.txtype.EX_CANCEL: {"version" : [self.__version_1], "block": 0}, \
                        self.txtype.EX_MARK  : {"version" : [self.__version_1], "block": 0}, \
                }

    @property
    def type_version(self):
        return self._type_version

    def _reset(self, payload):
        self.payload_hex= payload
        self.tx_version = 0
        self.tx_type = self.txtype.UNKNOWN
        self.op_code = self.optcodetype.OP_INVALIDOPCODE
        self.op_data = None
        self.op_size = 0
        self.op_mark = None
        self.proof_data = None
        self.is_valid = False

    @property
    def is_valid(self):
        return self.__is_valid

    @is_valid.setter
    def is_valid(self, value):
        self.__is_valid = value

    def txtype_map_proof_type(self, txtype):
        if txtype == self.txtype.EX_START or \
                txtype == self.txtype.EX_END or \
                txtype == self.txtype.EX_CANCEL:
            return "b"
        elif txtype == self.txtype.EX_MARK:
            return "v"
        else:
            return None

    #state is txtype
    @classmethod 
    def state_value_to_name(self, state):
        if state == self.txtype.EX_START:
            return "start"
        elif state == self.txtype.EX_CANCEL:
            return "cancel"
        elif state == self.txtype.EX_END:
            return "end"
        elif state == self.txtype.BTC_MARK:
            return "btcmark"
        elif state == self.txtype.EX_MARK:
            return "exmark"
        else:
            return "unkown"

    @classmethod
    def state_name_to_value(self, state):
        if state == "start":
            return self.txtype.EX_START
        elif state == "cancel":
            return self.txtype.EX_CANCEL
        elif state == "end":
            return self.txtype.EX_END
        elif state == "btcmark":
            return self.txtype.BTC_MARK
        elif state == "exmark":
            return self.txtype.EX_MARK
        else:
            return self.txtype.UNKNOWN

    @classmethod
    def state_value_to_txtype(self, value):
        try:
            return self.txtype(value)
        except Exception as e:
            pass
        return self.txtype.UNKNOWN

    @classmethod
    def is_bigendian(self):
        #0x0001
        val = array.array('H',[1]).tostring()
        if val[0] == 1:
            return False
        return True

    @property
    def valid_mark(self):
        return self.__valid_mark

    @property 
    def op_code(self):
        return self.__op_code

    @op_code.setter
    def op_code(self, code):
        self.__op_code = code

    @property
    def tx_version(self):
        return self.__txversion

    @tx_version.setter
    def tx_version(self, txversion):
        self.__txversion = txversion

    @property
    def tx_type(self):
        return self.__txtype

    @tx_type.setter
    def tx_type(self, txtype):
        self.__txtype = txtype

    @property
    def payload_hex(self):
        return self.__payload

    @payload_hex.setter
    def payload_hex(self, payload):
        self.__payload = payload

    @property
    def op_data(self):
        return self.__op_data

    @op_data.setter
    def op_data(self, data):
        self.__op_data = data

    @property
    def op_size(self):
        return self.__op_size 

    @op_size.setter
    def op_size(self, size):
        self.__op_size = size

    @property
    def op_mark(self):
        return self.__op_mark

    @op_mark.setter
    def op_mark(self, mark):
        self.__op_mark = mark

    @property
    def proof_data(self):
        return self.__proof_data 

    @proof_data.setter
    def proof_data(self, data):
        self.__proof_data  = data

    def reset(self):
        self.op_code = None
        self.op_data = None
        self.op_mark = None
        self.op_size = 0
        self.proof_data = None
        self.payload_hex = None
        self.tx_version = None
        self.tx_type = None

    def is_allow_mark(self, mark):
        return self.valid_mark == mark

    def is_allow_txtype(self, txtype):
        #EnumUtils.isValidEnum(self.txtype.class, txtype)
        return txtype.value in self.txtype._value2member_map_
    
    def is_allow_opreturn(self, txtype, version, block = None):
        type_version = self.type_version.get(txtype)
        if not self.is_allow_txtype(txtype):
            return False
        if type_version is None:
            return False
        if version not in type_version.get("version"):
            return False
        if block is not None and block < type_version.get("block"):
            return False

        return True

    def parse_data(self):
        try:
            if self.tx_type == self.txtype.EX_START:
                ret = parse_exchange.parse_ex_start(self.op_data)
            elif self.tx_type == self.txtype.EX_END:
                ret = parse_exchange.parse_ex_end(self.op_data)
            elif self.tx_type == self.txtype.EX_CANCEL:
                ret = parse_exchange.parse_ex_cancel(self.op_data)
            elif self.tx_type == self.txtype.BTC_MARK:
                ret = parse_exchange.parse_btc_mark(self.op_data)
            else:
                ret = result(error.TRAN_INFO_INVALID, f"tx type({self.tx_type.value}) is invalid.")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_valid_violas(self, payload):
        try:
            self.reset()
            ret = self.parse(payload)
            if ret.state != error.SUCCEED:
                return ret

            valid = self.is_valid
            ret = result(error.SUCCEED, "", valid)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parse(self, payload):
        try:
            self._logger.debug(f"payload:{payload}")
            self._reset(payload)
            bdata = bytes.fromhex(self.payload_hex)
            data_len = len(bdata)
            if bdata[0] != self.optcodetype.OP_RETURN.value:
                self._logger.debug(f"{bdata[0]} not OP_RETURN({self.optcodetype.OP_RETURN.value}) ")
                return result(error.ARG_INVALID, f"{bdata[0]} not OP_RETURN({self.optcodetype.OP_RETURN.value})")

            size = bdata[1]
            data_offer = 2 #0~n
            if size < self.optcodetype.OP_PUSHDATA1.value:
                data_offer = data_offer
            elif size == self.optcodetype.OP_PUSHDATA1.value:
                size = struct.unpack_from('>B', bdata, 2)[0]
                data_offer = data_offer + 1
            elif size == self.optcodetype.OP_PUSHDATA2.value:
                size = struct.unpack_from('>H', bdata, 2)[0]
                data_offer = data_offer + 2
            elif size == self.optcodetype.OP_PUSHDATA4.value:
                size = struct.unpack_from('>I', bdata, 2)[0]
                data_offer = data_offer + 4
            
            #OP_RETURN size(datas)
            self.op_size = size

            #opcode
            opcode_value = struct.unpack_from('B', bdata, 0)[0]
            self.op_code = self.optcodetype(opcode_value)

            #violas mark
            #makesure data is valid
            if data_offer + 6 >= data_len:
                return result(error.ARG_INVALID, "mark(violas) not found")

            try:
                mark = struct.unpack_from('cccccc', bdata, data_offer)
                self.op_mark = "".join([v.decode() for v in mark])
                data_offer = data_offer + 6
            except Exception as e:
                return result(error.ARG_INVALID, "get mark(violas) failed. maybe op_return's is not violas's format")


            if self.op_mark != self.valid_mark:
                return result(error.ARG_INVALID, f"mark({self.op_mark}) is not valid mark({self.valid_mark})")

            if data_offer + 2 >= data_len:
                return result(error.ARG_INVALID, "tx version not found.")

            self.tx_version = struct.unpack_from('>H', bdata, data_offer)[0]
            data_offer = data_offer + 2

            if data_offer + 2 >= data_len:
                return result(error.ARG_INVALID, "tx type not found.")

            tx_type = struct.unpack_from('>H', bdata, data_offer)[0]
            self.tx_type = self.state_value_to_txtype(tx_type)
            data_offer = data_offer + 2

            self.op_data = bdata[data_offer:]

            ret = self.parse_data()    
            if ret.state != error.SUCCEED:
                return ret

            self.proof_data = ret.datas
            self.is_valid = self.is_allow_opreturn(self.tx_type, self.tx_version) and self.is_allow_mark(self.op_mark)
            datas = {
                    "opcode" : self.op_code.name,
                    "datasize": self.op_size,
                    "mark" : self.op_mark,
                    "version": self.tx_version,
                    "type": self.tx_type.name,
                    "proof": self.proof_data,
                    "valid": self.is_valid,
                    }
            ret = result(error.SUCCEED, datas = datas) 
            self._logger.debug(json_dumps(datas))

        except Exception as e:
            ret = parse_except(e)
        return ret

    #b2v
    #open_return + violas 
#opstr = "6a4c5276696f6c617300003000f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000000001ed048cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
    
opstr = "6a4c5276696f6c617300003000f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"
#opstr = "6a4c5000027dbe00023efe054e8eead55dfc2f4d8699319e24ca0e9f5fee325b769d2b715457c163a9b3a9f769b376bf077f566ddf2cb85e180b6c050114edad1ca9a627de9305ad5bc9212a4ce706aebc7497"
    ###txid: f30a9f9497b97aa5f95a46f1bd6fceeb26241686526068c309dee8d8fafc0a97
    ###to_address:f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6 
    ###sequence: 20200110006
    ###token:cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2
   
def check(src, dest):
    return src == dest

def test_np():
    #dt = np.dtype(np.int32)
    global opstr

    pdata = payload(name)

    print(f"check op_return is valid: {pdata.is_valid_violas(opstr).datas}")
    ret = pdata.parse(opstr)
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed."
    
 
    


if __name__ == "__main__":
    test_np()
