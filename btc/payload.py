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
from comm.functions import json_reset
from comm.functions import json_print
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from .models import BtcRpc
from baseobject import baseobject
from enum import Enum

#module name
name="payload"
class payload(baseobject):
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

    def __init__(self, name, payload):
        baseobject.__init__(self, name)
        self.payload_hex= payload
        self.bigendian_flag = self.is_bigendian()
        self.tx_version = 0
        self.tx_type = self.txtype.UNKNOWN

        #parse
        self.parse()

    def is_bigendian(self):
        #0x0001
        val = array.array('H',[1]).tostring()
        if val[0] == 1:
            return False
        return True

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

    def is_allow_txtype(self, txtype):
        #EnumUtils.isValidEnum(self.txtype.class, txtype)
        return txtype in self.txtype._value2member_map_

    def parse(self):
        bdata = bytes.fromhex(self.payload_hex)
        if bdata[0] != self.optcodetype.OP_RETURN.value:
            self._logger.debug(f"{bdata[0]} not OP_RETURN({self.optcodetype.OP_RETURN.value}) ")
            return False
        size = struct.unpack_from('B', bdata, 2)[0]
        data_offer = 3 #0~n
        if size < self.optcodetype.OP_PUSHDATA1.value:
            pass
        if size == self.optcodetype.OP_PUSHDATA1.value:
            size = struct.unpack_from('>B', bdata, 2)[0]
            data_offer = data_offer + 1
        elif size == self.optcodetype.OP_PUSHDATA2.value:
            size = struct.unpack_from('>H', bdata, 2)[0]
            data_offer = data_offer + 2
        elif size == self.optcodetype.OP_PUSHDATA4.value:
            size = struct.unpack_from('>I', bdata, 2)[0]
            data_offer = data_offer + 4
        
        #opcode
        opcode_value = struct.unpack_from('B', bdata, 0)[0]
        opcode = self.optcodetype(opcode_value)

        #violas mark
        mark = struct.unpack_from('cccccc', bdata, data_offer)
        data_offer = data_offer + 6

        self.tx_version = struct.unpack_from('>H', bdata, data_offer)[0]
        data_offer = data_offer + 2
        self.tx_type= struct.unpack_from('>H', bdata, data_offer)[0]
        data_offer = data_offer + 2

        self._logger.debug(f"parse result: opcode = {opcode.name}, datasize = {size} mark = {mark} version = 0x{self.tx_version:02x}  type = 0x{self.tx_type:02x}")

        print(struct.unpack_from('BBBcccccc', bdata, 0))



    #b2v
    #open_return + violas 
opstr = "6a4c5276696f6c617300003000f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c600000000001ed048cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2"


def test_np():
    #dt = np.dtype(np.int32)
    global opstr
    pdata = payload(name, opstr)
    print(f"os is bigendian: {pdata.is_bigendian()}")
 


if __name__ == "__main__":
    test_np()
