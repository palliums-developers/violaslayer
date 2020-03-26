#!/usr/bin/python3
import operator
import sys, os
import json
import log
sys.path.append(os.getcwd())
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
getlogger = log.logger.getLogger
class baseobject(object):
    def __init__(self, name = 'base', work = True):
        self._name = None
        self._logger = None
        self._from_chain = None
        self._map_chain = None
        self._work = work
        self._name = name
        if self._logger is None:
            self._logger = getlogger(name) 

    def work(self):
        return self._work

    def work_stop(self):
        self._work = False

    def work_start(self):
        self._work = True

    def name(self):
        return self._name

    def from_chain(self):
        return self._from_chain

    def set_from_chain(self, name):
        self._from_chain = name

    def map_chain(self):
        return self._map_chain

    def set_map_chain(self, name):
        self._map_chain = name


