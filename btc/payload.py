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
#from .models import BtcRpc
from baseobject import baseobject
import btc.parse_exchange as parse_exchange
import btc.create_exchange as create_exchange
from enum import Enum
from ctypes import create_string_buffer
from comm.parseargs import parseargs

#module name
name="payload"
class payload(baseobject):
    __valid_mark = "violas"
    
    class versions(Enum):
        VERSION_0 = 0
        VERSION_1 = 1
        VERSION_2 = 2
        VERSION_3 = 3
        VERSION_4 = 4

    class optcodetype(Enum):
        # push value
        OP_0        = 0x00
        OP_FALSE    = OP_0
        OP_PUSHDATA1 = 0x4c
        OP_PUSHDATA2 = 0x4d
        OP_PUSHDATA4 = 0x4e
        OP_1NEGATE  = 0x4f
        OP_RESERVED = 0x50
        OP_1        = 0x51
        OP_TRUE     =0x51
        OP_2        = 0x52
        OP_3        = 0x53
        OP_4        = 0x54
        OP_5        = 0x55
        OP_6        = 0x56
        OP_7        = 0x57
        OP_8        = 0x58
        OP_9        = 0x59
        OP_10       = 0x5a
        OP_11       = 0x5b
        OP_12       = 0x5c
        OP_13       = 0x5d
        OP_14       = 0x5e
        OP_15       = 0x5f
        OP_16       = 0x60

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

    class txstate(Enum):
        START   = 0x0000
        CANCEL  = 0x0001
        END     = 0x0002
        STOP    = 0x0003
        BTCMARK = 0x0004
        MARK    = 0x0005
        UNKNOWN = 0xFFFF

    class txtype(Enum):
        BTCMARK= 0x1030
        MARK   = 0x2000
        B2VM    = 0x3000
        B2VUSD = 0x4000
        B2VEUR = 0x4010
        B2VSGD = 0x4020
        B2VGBP = 0x4030
        B2LUSD = 0x5000
        B2LEUR = 0x5010
        B2LSGD = 0x5020
        B2LGBP = 0x5030
        UNKNOWN= 0xFFFF

    class txcodetype(Enum):
        BTCMARK_BTCMARK = 0x1030
        MARK_MARK       = 0x2000
        #btc mapping violas btc
        B2VM_START       = 0x3000
        B2VM_CANCEL      = 0x3001
        B2VM_END         = 0x3002
        B2VM_STOP        = 0x3003
        #btc swap violas stable token
        B2VUSD_START    = 0x4000
        B2VUSD_CANCEL   = 0x4001
        B2VUSD_END      = 0x4002
        B2VUSD_STOP     = 0x4003
        B2VEUR_START    = 0x4010
        B2VEUR_CANCEL   = 0x4012
        B2VEUR_END      = 0x4013
        B2VEUR_STOP     = 0x4014
        B2VSGD_START    = 0x4020
        B2VSGD_CANCEL   = 0x4021
        B2VSGD_END      = 0x4022
        B2VSGD_STOP     = 0x4023
        B2VGBP_START    = 0x4030
        B2VGBP_CANCEL   = 0x4031
        B2VGBP_END      = 0x4032
        B2VGBP_STOP     = 0x4033
        #btc swap libra stable token
        B2LUSD_START    = 0x5000
        B2LUSD_CANCEL   = 0x5001
        B2LUSD_END      = 0x5002
        B2LUSD_STOP     = 0x5003
        B2LEUR_START    = 0x5010
        B2LEUR_CANCEL   = 0x5011
        B2LEUR_END      = 0x5012
        B2LEUR_STOP     = 0x5013
        B2LSGD_START    = 0x5020
        B2LSGD_CANCEL   = 0x5021
        B2LSGD_END      = 0x5022
        B2LSGD_STOP     = 0x5023
        B2LGBP_START    = 0x5030
        B2LGBP_CANCEL   = 0x5031
        B2LGBP_END      = 0x5032
        B2LGBP_STOP     = 0x5033
        UNKNOWN     = 0xFFFF

    def __init__(self, name, chain_id):
        baseobject.__init__(self, name)
        self.bigendian_flag = self.is_bigendian()
        self.__init_version()
        self.__init_type_with_version()
        self.__init__type_datas_parse()
        self._reset(None)
        self.__chain_id = chain_id
        

    class typeversions:
        def __init__(self):
            self.__datas= {}

        class blockrange:
            min_block = 0
            max_block = 0
            def __init__(self, min_block, max_block):
                self.min_block = min_block
                self.max_block = max_block

            def __repr__(self):
                return f"min_block = {self.min_block} max_block = {self.max_block}"

        @property
        def datas(self):
            return self.__datas

        def copy(self, datas):
            self.__datas = datas.datas

        def update(self, tv, version, min_block = 0, max_block = 0):
            self.datas.get(tv, {}).update(self.create_version_info(version, min_block, max_block))

        def set(self, tv, datas):
            self.clear(tv)
            self.datas.update({tv: {}})
            if isinstance(datas, dict):
                self.datas.update({tv:datas})
            elif isinstance(datas, list):
                for item in datas: self.datas[tv].update(item);

        def get(self, tv):
            return self.datas.get(tv, {})

        def clear(self, tv = None):
            if tv:
                if tv in self.datas: del self.datas[tv];
            else:
                self.datas.clear()

        def get_block_range(self, tv, version):
            return self.get(tv).get(version)

        def is_valid(self, tv, version, block = 0):

            block_range = self.get_block_range(tv, version)
            print(f"tv = {tv} version = {version}, block_range = {block_range}")
            if block is None: block = 0;

            if block_range:
                return block >= block_range.min_block and (block <= block_range.max_block or block_range.max_block == 0)
            return False

        @classmethod
        def create_version_info(self, version, min_block = 0, max_block = 0):
            return {version:self.blockrange(min_block, max_block)}


    def __init_type_with_version(self):
        self._type_version = self.typeversions()
        #start support version_4, other support version_3 version_4
        start_versions  = [self.typeversions.create_version_info(self.version_4)]
        end_versions    = [
                self.typeversions.create_version_info(self.version_3, 0, 0),
                self.typeversions.create_version_info(self.version_4, 0, 0),
                ]
        stop_versions   = list(end_versions)
        cancel_versions = list(end_versions)
        mark_versions = [self.typeversions.create_version_info(version.value, 0, 0) for version in self.versions]

        for tv in self.txcodetype:
            if tv.name.endswith("_START"):
                self.type_version.set(tv, start_versions)
            elif tv.name.endswith("_END"):
                self.type_version.set(tv, end_versions)
            elif tv.name.endswith("_STOP"):
                self.type_version.set(tv, stop_versions)
            elif tv.name.endswith("MARK"):
                self.type_version.set(tv, mark_versions)

    def __init__type_datas_parse(self):
        self._type_funcs = {}
        for txcodetype in self.txcodetype:
            if txcodetype != self.txcodetype.UNKNOWN:
                state = self.get_state_from_txcodetype(txcodetype)
                if state == self.txstate.START:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_ex_start})
                elif state == self.txstate.CANCEL:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_ex_cancel})
                elif state == self.txstate.END:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_ex_end})
                elif state == self.txstate.STOP:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_ex_stop})
                elif state == self.txstate.MARK:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_ex_mark})
                elif state == self.txstate.BTCMARK:
                    self.type_funcs.update({txcodetype : parse_exchange.parse_btc_mark})
                else:
                    raise Exception("not found state({state}) function.")

    def __init_version(self):
        for item in self.versions:
            setattr(self, item.name.lower(), item.value)
            setattr(self, "version", item.value)


    def _reset(self, payload):
        self.payload_hex= payload
        self.tx_version = 0
        self.tx_type = self.txtype.UNKNOWN
        self.tx_codetype = self.txcodetype.UNKNOWN
        self.tx_state = self.txstate.UNKNOWN
        self.op_code = self.optcodetype.OP_INVALIDOPCODE
        self.op_data = None
        self.op_size = 0
        self.op_mark = None
        self.proof_data = None
        self.is_valid = False

    @property
    def type_funcs(self):
        return self._type_funcs

    @property
    def type_version(self):
        return self._type_version

    @property
    def is_valid(self):
        return self.__is_valid

    @is_valid.setter
    def is_valid(self, value):
        self.__is_valid = value

    #state is txstate
    @classmethod 
    def state_value_to_name(self, state):
        return state.name.lower()

    @classmethod
    def state_name_to_value(self, state):
        return self.txstate[state.upper()]
       
    @classmethod
    def type_value_to_name(self, value):
        return value.name.lower()

    @classmethod
    def type_name_to_name(self, value):
        return self.txtype[value.upper()]

    @classmethod
    def type_value_to_txtype(self, value):
        try:
            return self.txtype(value)
        except Exception as e:
            pass
        return self.txtype.UNKNOWN

    @classmethod
    def codetype_value_to_txcodetype(self, value):
        try:
            return self.txcodetype(value)
        except Exception as e:
            pass
        return self.txcodetype.UNKNOWN

    @classmethod
    def compose_txcodetype(self, left, right):
        return self.txcodetype[f"{left.upper()}_{right.upper()}"]

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
    def tx_codetype(self):
        return self.__txcodetype

    @tx_codetype.setter
    def tx_codetype(self, txcodetype):
        self.__txcodetype = txcodetype

    @property
    def tx_state(self):
        return self.__txstate

    @tx_state.setter
    def tx_state(self, txstate):
        self.__txstate = txstate
        
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

    @property
    def parse_result(self):
        return self.__parse_result

    @parse_result.setter
    def parse_result(self, value):
        self.__parse_result = value

    def reset(self):
        self.op_code = None
        self.op_data = None
        self.op_mark = None
        self.op_size = 0
        self.proof_data = None
        self.payload_hex = None
        self.tx_version = None
        self.tx_type = None
        self.tx_state = None

    def get_state_from_txcodetype(self, txcodetype):
        if txcodetype == self.txcodetype.UNKNOWN:
            return self.txstate.UNKNOWN

        type_state = txcodetype.name.lower().split("_")
        assert len(type_state) == 2, f"txcodetype({txcodetype.name}) is invalid."
        state = type_state[1]
        return self.txstate[state.upper()]

    def get_type_from_txcodetype(self, txcodetype):
        if txcodetype == self.txcodetype.UNKNOWN:
            return self.txstate.UNKNOWN

        type_state= txcodetype.name.lower().split("_")
        assert len(type_state) == 2, f"txcodetype({txcodetype.name}) is invalid."
        txtype = type_state[0]
        return self.txtype[txtype.upper()]

    def is_allow_mark(self, mark):
        return self.valid_mark == mark

    def is_allow_txtype(self, txtype):
        #EnumUtils.isValidEnum(self.txtype.class, txtype)
        return txtype.value in self.txtype._value2member_map_ and txtype != self.txtype.UNKNOWN
    
    def is_allow_txcodetype(self, txcodetype):
        #EnumUtils.isValidEnum(self.txcodetype.class, txcodetype)
        return txcodetype.value in self.txcodetype._value2member_map_ and txcodetype != self.txcodetype.UNKNOWN

    def is_allow_opreturn(self, txcodetype, version, block = None):
        if not self.is_allow_txcodetype(txcodetype):
            return False

        return self.type_version.is_valid(txcodetype, version, block) 


    def is_allow_chain_id(self, txcodetype, version, chain_id):
        if version >= self.version_4 and txcodetype.endswith("_START"):
            return chain_id is not None and self.chain_id == chain_id
        return True

    def parse_data(self):
        try:
            if self.tx_codetype in self.type_funcs:
                ret = self.type_funcs[self.tx_codetype](self.op_data)
            else:
                ret = result(error.TRAN_INFO_INVALID, f"tx type({self.tx_codetype.value}) is invalid.")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_valid_violas(self, payload, block=None):
        try:
            self.reset()
            ret = self.parse(payload, block)
            if ret.state != error.SUCCEED:
                return ret

            valid = self.is_valid
            ret = result(error.SUCCEED, "", valid)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def get_data_size_offer(self, bdata, fixsize):
        try:
            data_offer = 0
            size = fixsize
            offer = 0
            if size < self.optcodetype.OP_PUSHDATA1.value:
                data_offer = 0
            elif size == self.optcodetype.OP_PUSHDATA1.value:
                size = struct.unpack_from('>B', bdata, offer)[0]
                data_offer = data_offer + 1
            elif size == self.optcodetype.OP_PUSHDATA2.value:
                size = struct.unpack_from('>H', bdata, offer)[0]
                data_offer = data_offer + 2
            elif size == self.optcodetype.OP_PUSHDATA4.value:
                size = struct.unpack_from('>I', bdata, offer)[0]
                data_offer = data_offer + 4
            else:
                return result(error.ARG_INVALID, f"opt code type is not in {self.optcodetype}")

            ret = result(error.SUCCEED, "", (size, data_offer))
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
            ret = self.get_data_size_offer(bdata[2:], size)
            if ret.state != error.SUCCEED:
                return ret

            size, offer = ret.datas
            data_offer += offer
            
            #OP_RETURN size(datas)
            self.op_size = size

            #opcode
            opcode_value = struct.unpack_from('B', bdata, 0)[0]
            self.op_code = self.optcodetype(opcode_value)

            ret = self.parse_opt_data(bdata[data_offer:])
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parse_opt_datahex(self, data, block = None):
        try:
            self._reset(data)
            self.payload_hex = data
            bdata = bytes.fromhex(data)
            ret = self.parse_opt_data(bdata, block)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def parse_opt_data(self, bdata, block):
        try:
            #violas mark
            #makesure data is valid
            data_offer = 0
            data_len = len(bdata)
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

            tx_codetype = struct.unpack_from('>H', bdata, data_offer)[0]
            self.tx_codetype = self.codetype_value_to_txcodetype(tx_codetype)
            self.tx_state = self.get_state_from_txcodetype(self.tx_codetype)
            self.tx_type = self.get_type_from_txcodetype(self.tx_codetype)
            data_offer = data_offer + 2

            self.op_data = bdata[data_offer:]

            ret = self.parse_data()    
            if ret.state != error.SUCCEED:
                return ret

            self.proof_data = ret.datas
            self.is_valid = self.is_allow_opreturn(self.tx_codetype, self.tx_version, block) \
                    and self.is_allow_mark(self.op_mark) \
                    and self.is_allow_chain_id(self.tx_codetype, self.tx_version, self.proof_data.get("chain_id"))
            datas = {
                    "opcode" : self.op_code.name,
                    "datasize": self.op_size,
                    "mark" : self.op_mark,
                    "version": self.tx_version,
                    "type": self.tx_type.name,
                    "state": self.tx_state.name,
                    "proof": self.proof_data,
                    "valid": self.is_valid,
                    "codetype": self.tx_codetype.value,
                    }
            self.parse_result = datas
            ret = result(error.SUCCEED, datas = datas) 
            self._logger.debug(json_dumps(datas))

        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def get_bytes_compact_size(self, size):
        compact_size = 0
        if size < self.optcodetype.OP_PUSHDATA1.value:
            compact_size = 1
        elif size < 0xff:
            compact_size = 2
        elif size < 0xffff:
            compact_size = 3
        else:
            compact_size = 5
        return compact_size 

    def create_opt_buf(self, size):
        try:
            datas = None
            data_offer = 0
            datas = create_string_buffer(size)

            ret = result(error.SUCCEED, "", (data_offer, datas))
        except Exception as e:
            ret = parse_except(e)
        return ret
    def create_payload(self, txver, txcodetype, data):
        try:
            # mark.size + ver.size + txcodetype.sizde + data.size
            size = len(self.valid_mark) + 2 + 2 + len(data)
            ret = self.create_opt_buf(size)
            if ret.state != error.SUCCEED:
                return ret

            offer, datas = ret.datas

            struct.pack_into(f">{len(self.valid_mark)}sHH", datas, offer, 
                    str.encode(self.valid_mark),
                    txver,
                    txcodetype.value
                    )

            index = offer + len(self.valid_mark) + 4
            for c in data:
                datas[index] = c
                index += 1

            redatas = struct.unpack_from(f"{len(datas)}s", datas, 0)[0]
            ret = result(error.SUCCEED, "", redatas.hex())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_ex_start(self, swap_type, toaddress, sequence, module, outamount, times, chainid):
        try:
            ret = create_exchange.create_ex_start(toaddress, sequence, module, outamount, times, chainid)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.compose_txcodetype(swap_type, "start")
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def create_ex_cancel(self, swap_type, toaddress, sequence):
        try:
            ret = create_exchange.create_ex_cancel(toaddress, sequence)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.compose_txcodetype(swap_type, "cancel")
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def create_ex_end(self, swap_type, toaddress, sequence, amount, version):
        try:
            ret = create_exchange.create_ex_end(toaddress, sequence, amount, version)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.compose_txcodetype(swap_type, "end")
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def create_ex_stop(self, swap_type, toaddress, sequence):
        try:
            ret = create_exchange.create_ex_stop(toaddress, sequence)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.compose_txcodetype(swap_type, "stop")
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def create_ex_mark(self, toaddress, sequence, version, amount):
        try:
            ret = create_exchange.create_ex_mark(toaddress, sequence, version, amount)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.txcodetype.MARK_MARK
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def create_btc_mark(self, swap_type, toaddress, sequence, amount, name):
        try:
            ret = create_exchange.create_btc_mark(toaddress, sequence, amount, name)
            if ret.state != error.SUCCEED:
                return ret
            
            txcodetype = self.txcodetype.BTCMARK_BTCMARK
            #txcodetype = self.compose_txcodetype(swap_type, "btcmark")
            ret = self.create_payload(self.version, txcodetype, ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    #b2v
    #open_return + violas 
    
