#!/usr/bin/python3
import os, sys
#import setting
from comm import result
from comm.result import parse_except
from comm.functions import json_print

from tomlbase import tomlbase


class tomlopt(tomlbase):
    def __init__(self, tomlfile):
        super().__init__(tomlfile)

    def get(self, key):
        return self.content[key]

    @property
    def looping_sleep(self):
        return self.get("looping_sleep")

    @property
    def db_list(self):
        return self.get("db_list")

    @property
    def btc_conn(self):
        return self.get("btc_conn")

    @property
    def traceback_limit(self):
        return self.get("traceback_limit")

setting = tomlopt("violaslayer.toml")


def check_setting():
    pass

def get_looping_sleep(mtype):
    try:
        sleep = setting.looping_sleep.get(mtype, 1)
    except Exception as e:
        sleep = 1
    return sleep


def get_db(mtype):
    try:
        dbs = [dict for dict in setting.db_list if dict.get("db") == mtype and mtype is not None]
        if len(dbs) > 0:
            return dbs[0]
    except Exception as e:
        parse_except(e)
    return None

def list_db_name():
    try:
        dbs = [dict.get("db") for dict in setting.db_list]
        if len(dbs) > 0:
            return dbs
    except Exception as e:
        parse_except(e)
    return None

def get_btc_conn():
    try:
        return setting.btc_conn
    except Exception as e:
        parse_except(e)
    return None

def get_traceback_limit():
    try:
        return setting.traceback_limit
    except Exception as e:
        parse_except(e)
    return 0

def get_conf():
    infos = {}
    mtypes = ["base", "b2vproof", "markproof"]
    for mtype in mtypes:
        info = {}
        info["db"] = get_db(mtype)
        info["loop sleep"] = get_looping_sleep(mtype)
        infos[mtype] = info
    infos["traceback limit"] = get_traceback_limit()
    infos["btc conn"] = get_btc_conn()
    return infos

def main():
    datas = get_conf()
    json_print(datas)



if __name__ == "__main__":
    main()
