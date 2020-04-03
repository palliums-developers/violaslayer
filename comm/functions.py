#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc and vbtc exchange main
'''
import operator
import signal
import sys, os
import log
import json, decimal
import log.logger
import threading
import subprocess
import fcntl

def checkrerun(rfile):
    print(f"*************************{rfile}")
    proc = subprocess.Popen(["pgrep", "-f", rfile], stdout=subprocess.PIPE)
    std = proc.communicate()
    if len(std[0].decode().split()) > 1:
        exit("already running")

def write_pid(name):
    try:
        f = open(f"{name}.pid", mode='w')
        f.write(f"{os.getpid()}\n")
        f.close()
    except Exception as e:
        parse_except(e)

def pid_name(name):
    return f"{name}.pid"

class filelock:
    def __init__(self, name):
        self.fobj = open(pid_name(name), 'w')
        self.fd = self.fobj.fileno()

    def __del__(self):
        self.unlock()
    def lock(self):
        try:
            fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except Exception as e:
            return False

    def unlock(self):
        try:
            self.fobj.close()
        except Exception as e:
            pass


class FancyFloat(float):
    def __repr__(self):
        return format(Decimal(self), "f")

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
           return float(o)
         
        super().default(o)

def json_print(data):
    if data is None:
        print("")
    print(json.dumps(data, sort_keys=True, cls= DecimalEncoder, indent=5))

def json_reset(data):
    if data is None:
        return {}
    return json.loads((json.dumps(data, sort_keys=True, cls= DecimalEncoder, indent=5)))
