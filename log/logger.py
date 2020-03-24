import logging
import logging.config
import log.config


def __init__():
    print("logger.__init__")

def getLogger(name):

    log.config.config["handlers"]["file"]["filename"]=f"{name}.log"
    default = log.config.config.get("loggers").get("bvelog")
    if name not in log.config.config.get("loggers"):
        log.config.config.get("loggers")[name] = default

    #default = log.config.config.get("loggers").get("bvelog")
    #file_tmp = dict(log.config.config["handlers"].get("file"))
    #file_tmp.update("filename", f"{name}.log")
    #log.config.config.get("loggers").update(name, {"handlers":['console', name], 'level':default.get("level")})

    logging.config.dictConfig(log.config.config)
    logger = logging.getLogger(name)

    return logger

