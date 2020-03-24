#!/usr/bin/python3
import setting
from comm import result
from comm.result import parse_except

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
        if dbs is not None and len(dbs) > 0:
            return dbs[0]
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
    mtypes = ["v2b", "v2l", "l2v", "b2v", "vfilter", "lfilter"]
    for mtype in mtypes:
        info = {}
        info["db"] = get_db(mtype)
        info["loop sleep"] = get_looping_sleep(mtype)
        infos[mtype] = info
    infos["traceback limit"] = get_traceback_limit()
    infos["btc conn"] = get_btc_conn()
    return infos

def main():
    pass

if __name__ == "__main__":
    main()
