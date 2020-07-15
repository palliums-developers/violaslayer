#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc transactions and proof main
'''
import operator
import signal
import sys, os
import traceback
import log
import log.logger
import threading
import stmanage
from time import sleep, ctime
import comm.functions as fn
from comm.result import parse_except
from analysis import analysis_filter, analysis_proof, analysis_mark
from btc.payload import payload
import subprocess
from enum import Enum

name="violaslayer"


class works:
    __threads = []
    __work_looping = {}
    __work_obj = {}

    __btc_min_valid_version     = 161_2270
    def __init__(self):
        logger.debug("works __init__")
        for mod in self.__work_looping:
            self.__work_looping[mod.name] = 1

        self.__threads = []

    def __del__(self):
        del self.__threads

    def set_work_obj(self, obj):
        old_obj = self.__work_obj.get(obj.name())
        if old_obj is not None:
            del old_obj

        if obj.name() in self.__work_obj:
            del self.__work_obj[obj.name()]

        self.__work_obj[obj.name()] = obj

    def work_bfilter(self, nsec):
        try:
            logger.critical("start: btc filter")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug("looping: btc filter")
                try:
                    obj = analysis_filter.afilter(name="bfilter",  \
                            dbconf=stmanage.get_db("base"), \
                            nodes=stmanage.get_btc_conn())
                    obj.set_min_valid_version(self.__btc_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: bload")

    def work_b2vproof(self, nsec):
        try:
            logger.critical("start: btc b2v proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug(f"looping: {mod}")
                try:
                    basedata = "base"
                    obj = analysis_proof.aproof(name="b2vproof", \
                            dbconf=stmanage.get_db(dtype), \
                            fdbconf=stmanage.get_db(basedata), \
                            nodes = stmanage.get_btc_conn() \
                            )
                    obj.append_valid_txtype(payload.txtype.EX_CANCEL)
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: b2vproof")

    def work_markproof(self, nsec):
        try:
            logger.critical("start: mark proof")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            #libra transaction's data types 
            dtype = self.get_dtype_from_mod(mod)
            while (self.__work_looping.get(mod, False)):
                logger.debug("looping: markproof")
                try:
                    basedata = "base"
                    obj = analysis_mark.amarkproof(name="markproof", \
                            dbconf=stmanage.get_db(dtype), \
                            fdbconf=stmanage.get_db(basedata), \
                            nodes = stmanage.get_btc_conn() \
                            )
                    obj.append_valid_txtype(payload.txtype.BTCMARK_BTCMARK)
                    obj.append_valid_txtype(payload.txtype.V2BMARK_MARK)
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: markproof")

    def work_comm(self, nsec):
        try:
            logger.critical("start: comm")
            nsec = kargs.get("nsec", 0)
            mod = kargs.get("mod")
            assert mod is not None, f"mod name is None"

            while(self.__work_looping.get(mod, False)):
                logger.debug("looping: comm")
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: comm")

    class work_thread(threading.Thread):
        __name = ""
        __threadId = 0
        __nsec = 1
        __work = ""
        def __init__(self, work, threadId, name, **kwargs):
            logger.debug("work thread __init__: name = %s  nsec = %i" ,name, nsec)
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__kwargs = kwargs
            self.__work = work

        def run(self):
            logger.debug(f"work thread run{self.__kwargs}")
            self.__work(**self.__kwargs)

    def get_dtype_from_mod(self, modname):
        dtype = modname.lower()
        if dtype[:3] in ["b2l", "b2v"]:
            if dtype.endswith("proof"):
                return dtype[:-5]
        return dtype

    def thread_append(self, work, mod):
        try:
            #b2v = self.work_thread(work, threadId, name, nsec)
            obj = self.work_thread(work, mod.value, mod.name.lower(), \
                    stmanage.get_looping_sleep(mod.name.lower()), \
                    mod = mod.name.lower())
            self.__threads.append(obj)
        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("thread_append")

    def create_func_dict(self, mod, func):
        return {mod.name.lower() : func}

    @property
    def funcs_map(self):
        return self.__funcs_map

    def init_func_map(self):
        self.__funcs_map = {}
        #append proof
        for item in work_mod:
            name = item.name
            if name == "BFILTER":
                self.__funcs_map.update(self.create_func_dict(item, self.work_bfilter))
            elif name == "B2VPROOF":
                self.funcs_map.update(self.create_func_dict(item, self.work_b2vproof))
            elif name.startswith("B2V") and len(name) == 8 and name.endswith("PROOF"):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2vmapproof))
            elif name.startswith("B2L") and len(name) == 11 and name.endswith("PROOF"):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2vswapproof))
            elif name.startswith("B2V") and len(name) == 11 and name.endswith("EX"):
                self.__funcs_map.update(self.create_func_dict(item, self.work_b2lswapproof))
            elif name == "COMM":
                self.__funcs_map.update(self.create_func_dict(item, self.work_comm))
            else:
                logger.warning(f"not matched function:{item}")

    def start(self, work_mods):
        try:
            logger.debug("start works")

            self.__work_looping = work_mods

            for name, state in work_mods.items():
                if state:
                    self.thread_append(self.funcs_map[name.lower()], work_mod[name.upper()])

            for work in self.__threads:
                work.start() #start work

        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("start end")

    def join(self):
        try:
            logger.debug("start join")

            for work in self.__threads:
                work.join() # work finish
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("end join")

    def stop(self):
        logger.debug("stop works")
        for mod in self.__work_looping.keys():
            self.__work_looping[mod] = False

        for key in self.__work_obj:
            obj = self.__work_obj.get(key)
            if obj is not None:
                obj.stop()

class work_mod(Enum):
    COMM        = 0
    BFILTER     = 1
    MARKPROOF   = 2
    B2VPROOF    = 4
    B2VUSDPROOF    = 10
    B2VEURPROOF    = 11
    B2VSGDPROOF    = 12
    B2VGBPPROOF    = 13
    B2lUSDPROOF    = 20
    B2lEURPROOF    = 21
    B2lSGDPROOF    = 22
    B2lGBPPROOF    = 23

logger = log.logger.getLogger(name)
work_manage = works()
def signal_stop(signal, frame):
    try:
        logger.debug("start signal : %i", signal )
        global work_manage
        work_manage.stop()
    except Exception as e:
        parse_except(e)
    finally:
        logger.debug("end signal")

def list_valid_mods():
    valid_mods = ["all"]
    for mod in work_mod:
        valid_mods.append(mod.name.lower())
    return valid_mods

def run(mods):
    stmanage.reset()

    valid_mods = list_valid_mods()
    for mod in mods:
        if mod is None or mod not in valid_mods:
            raise Exception(f"mod({mod}) is invalid {valid_mods}.")

    #fn.checkrerun(__file__)
    fn.write_pid(name)
    lockpid = fn.filelock(name)
    if lockpid.lock() == False:
        logger.warning("already running.")
        sys.exit(0)

    global work_manage
    logger.debug("start main")
    
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)
    work_mods = {}
    for mod in mods:
        work_mods[mod.upper()] = True
        if mod == "all":
            for wm in work_mod:
                work_mods[wm.name.upper()] = True
            break

    logger.critical(f"work_mods= {work_mods}")
    work_manage.start(work_mods)
    work_manage.join()

def main(argc, argv):
    try:
        if argc < 1:
             raise Exception(f"argument is invalid")
        run(argv)
    except Exception as e:
        parse_except(e)
    finally:
        logger.critical("main end")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
