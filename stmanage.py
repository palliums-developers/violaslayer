#!/usr/bin/python3
import os, sys
#import setting
from comm import result
from comm.result import parse_except
from comm.functions import json_print
from dataproof.dataproof import setting

def check_setting():
    pass

def set_conf_env_default():
    setting.setting.set_conf_env_default()
    reset()

def set_conf_env(conffile):
    setting.setting.set_conf_env(conffile)
    reset()

def reset():
    setting.setting.reset()

def get_conf_env():
    return setting.setting.get_conf_env()

def is_loaded_conf():
    return setting.setting.is_loaded

def get_looping_sleep(mtype):
    try:
        sleep = setting.setting.looping_sleep.get(mtype, 1)
    except Exception as e:
        sleep = 1
    return sleep


def get_db(mtype):
    try:
        dbs = [dict for dict in setting.setting.db_list if dict.get("db") == mtype and mtype is not None]
        if len(dbs) > 0:
            return dbs[0]
    except Exception as e:
        parse_except(e)
    return None

def list_db_name():
    try:
        dbs = [dict.get("db") for dict in setting.setting.db_list]
        if len(dbs) > 0:
            return dbs
    except Exception as e:
        parse_except(e)
    return None

def get_btc_conn():
    try:
        return setting.setting.btc_conn
    except Exception as e:
        parse_except(e)
    return None

def get_traceback_limit():
    try:
        return setting.setting.traceback_limit
    except Exception as e:
        parse_except(e)
    return 0

def get_chain_id():
    try:
        return setting("chain_id")
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
    infos["chain id"] = get_chain_id()
    return infos

def main():
    set_conf_env("./violaslayer.toml")
    reset()
    
    datas = get_conf()
    json_print(datas)



if __name__ == "__main__":
    main()
