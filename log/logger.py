import logging
import logging.config
import log.config

import os
import threading

lock = threading.Lock()

log_path = "./datas/logs"

def __init__():
    print("logger.__init__")

def getLogger(name):

    lock.acquire()
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    hfile = dict(log.config.config["handlers"]["file"])
    hfile["filename"]=f"{log_path}/{name}.log"
    log.config.config["handlers"].update({name:hfile})
    default = log.config.config.get("loggers").get("bvelog")
    if name not in log.config.config.get("loggers"):
        new_logger = dict(default)
        new_logger["handlers"] = ["console", name]
        log.config.config["loggers"].update({name:new_logger})

    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger(name)
    lock.release()

    return logger

