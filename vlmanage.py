#!/usr/bin/python3
import sys, getopt, os
import log 
import json
import stmanage
import log.logger
import violaslayer
from comm.parseargs import parseargs

#from tools import show_workenv

name = "violaslayer"
logger = log.logger.getLogger(name)


def init_args(pargs):
    pargs.append("help", "show args info")
    pargs.append("conf", "config file path name. default:violaslayer.toml", True, "toml file")
    pargs.append("mod", "run mod", True, violaslayer.list_valid_mods())
    #pargs.append("info", "show info", True, show_workenv.list_valid_mods())

def main(argc, argv):
    pargs = parseargs()
    try:
        logger.debug("start manage.main")
        init_args(pargs)
        pargs.show_help(argv)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(str(e))
        sys.exit(2)
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)

    if err_args is None or len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    #--conf must be first
    for opt, arg in opts:
        if pargs.is_matched(opt, ["conf"]):
            stmanage.set_conf_env(arg)
            break
    if stmanage.get_conf_env() is None:
        stmanage.set_conf_env_default() 

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(arg)
        if pargs.is_matched(opt, ["mod"]) :
            if count < 1:
                pargs.exit_error_opt(opt)
            logger.debug(f"arg_list:{arg_list}")
            violaslayer.run(arg_list)

        if pargs.is_matched(opt, ["info"]) :
            if count < 1:
                pargs.exit_error_opt(opt)
            logger.debug(f"arg_list:{arg_list}")
            show_workenv.run(arg_list)
    logger.debug("end manage.main")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
