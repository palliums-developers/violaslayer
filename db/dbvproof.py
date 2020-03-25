#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import redis
import json
from comm.error import error
from comm.result import result, parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String
from db.dbvbase import dbvbase

from enum import Enum

#module name
name="dbvproof"

#load logging

class dbvproof(dbvbase):
    __KEY_MIN_VERSION_START = "min_version_start"
    def __init__(self, name, host, port, db, passwd = None):
        dbvbase.__init__(self, name, host, port, db, passwd)

    def __del__(self):
        dbvbase.__del__(self)

    def set_proof(self, version, value):
        try:
            dict = json.loads(value)
            tran_id = dict.get("tran_id", None)
            if tran_id is None or len(tran_id) <= 0:
                return result(error.ARG_INVALID, "tran id is invalid.")

            ret = self.set(version, value)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.set(tran_id, version)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_by_hash(self, tran_id):
        try:
            ret = self.get(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            version = ret.datas
            if version is None or len(version) == 0:
                return result(error.TRAN_INFO_INVALID, f"not found proof, tran_id: {tran_id}.")
            
            return self.get(ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def get_proof_version(self, version):
        try:
            return self.get(version)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_proof_min_version_for_start(self, version):
        try:
            ret = self.set(self.__KEY_MIN_VERSION_START, version)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_min_version_for_start(self):
        try:
            ret = self.get(self.__KEY_MIN_VERSION_START)
            if ret.state == error.SUCCEED:
                if ret.datas is None:
                    ret = result(error.SUCCEED, "", '0')
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_haddress_name(self, tran_info):
        return f"{tran_info['sender']}_{tran_info['flag']}"

    def create_haddress_key(self, tran_info):
        return f"{tran_info['version']}"

    def create_haddress_value(self, tran_info):
        return json.dumps({"version":tran_info["version"], "type":tran_info["type"], "state":tran_info["state"], "to_address":tran_info["to_address"], "amount":tran_info["amount"]})
