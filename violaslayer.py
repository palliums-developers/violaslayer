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
from analysis import analysis_filter 
import subprocess
from enum import Enum

name="violaslayer"

class work_mod(Enum):
    COMM        = 0
    BFILTER     = 1
    B2VPROOF    = 2
    MARK        = 3

class works:
    __threads = []
    __work_looping = {}
    __work_obj = {}

    __btc_min_valid_version     = 0
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
            while (self.__work_looping.get(work_mod.BFILTER.name, False)):
                logger.debug("looping: btc filter")
                try:
                    dtype = "bfilter"
                    obj = analysis_filter.afilter(name="bfilter",  \
                            dbconf=stmanage.get_db("base"), \
                            nodes=stmanage.get_btc_conn())
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                break
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: bload")

    def work_proof(self, nsec):
        try:
            logger.critical("start: btc b2v proof")
            while (self.__work_looping.get(work_mod.B2VPROOF.name, False)):
                logger.debug("looping: b2vproof")
                try:
                    dtype = "b2v"   #libra transaction's data types 
                    basedata = "bfilter"
                    obj = analysis_proof.aproof(name="b2vproof", dtype=dtype, \
                            dbconf=stmanage.get_db(dtype), fdbconf=stmanage.get_db(basedata))
                    obj.set_step(stmanage.get_db(dtype).get("step", 100))
                    obj.set_min_valid_version(self.__btc_min_valid_version - 1)
                    self.set_work_obj(obj)
                    obj.start()
                except Exception as e:
                    parse_except(e)
                sleep(nsec)
        except Exception as e:
            parse_except(e)
        finally:
            logger.critical("stop: v2lproof")

    def work_comm(self, nsec):
        try:
            logger.critical("start: comm")
            while(self.__work_looping.get(work_mod.COMM.name, False)):
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
        def __init__(self, work, threadId, name, nsec):
            logger.debug("work thread __init__: name = %s  nsec = %i" ,name, nsec)
            threading.Thread.__init__(self)
            self.__threadId = threadId
            self.__name = name
            self.__nsec = nsec
            self.__work = work

        def run(self):
            logger.debug("work thread run")
            self.__work(self.__nsec)

    def thread_append(self, work, mod):
        try:
            #b2v = self.work_thread(work, threadId, name, nsec)
            obj = self.work_thread(work, mod.value, mod.name.lower(), stmanage.get_looping_sleep(mod.name.lower()))
            self.__threads.append(obj)
        except Exception as e:
            parse_except(e)
        finally:
            logger.debug("thread_append")

    def start(self, work_mods):
        try:
            logger.debug("start works")

            self.__work_looping = work_mods

            self.thread_append(self.work_comm, work_mod.COMM)

            if work_mods.get(work_mod.BFILTER.name, False):
                self.thread_append(self.work_bfilter, work_mod.BFILTER)

            if work_mods.get(work_mod.B2VPROOF.name, False):
                self.thread_append(self.work_b2vproof, work_mod.B2VPROOF)

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
