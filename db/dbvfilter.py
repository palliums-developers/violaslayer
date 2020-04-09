#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import random
import redis
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
name="dbvfilter"

class dbvfilter(dbvbase):
    def __init__(self, name, host,  db, passwd = None):
        dbvbase.__init__(self, name, port, db, passwd)

    def __del__(self):
        dbvbase.__del__(self)

