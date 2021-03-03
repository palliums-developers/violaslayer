#!/usr/bin/python3
import sys, getopt, os
import log 
import json
import stmanage
import log.logger
import violaslayer
from comm.parseargs import parseargs
from dataproof import dataproof
#from tools import show_workenv

name = "violaslayer"
logger = log.logger.getLogger(name)


def show_exec_args():
    logger.info(f"conf -- conf file(toml): {stmanage.get_conf_env()}")
    [logger.info(f'conf -- {key}: {dataproof.configs(key)}') for key in dataproof.configs.datas]
    fields = []
    for field in fields:
        logger.info(f'conf -- {field}: dataproof.configs({field})')

def raise_with_check_conf():
    if not stmanage.is_loaded_conf():
        raise Exception(f"not found conf file")

def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show args info", priority = 11)
    pargs.append("conf", "config file path name. default:violaslayer.toml", True, "toml file", priority = 10)
    pargs.append("chainid", "set violas chain id[4 | 5] default = 4", True, "chain id", priority = 12)
    pargs.append("mod", "run mod", True, violaslayer.list_valid_mods() if stmanage.get_conf_env() is not None else "args from conf file")
    pargs.append(show_exec_args, "show exec args")
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

    for opt, arg in opts:
        count, arg_list = pargs.split_arg(opt, arg)
        if pargs.is_matched(opt, ["conf"]):
            stmanage.set_conf_env(arg)
        elif pargs.is_matched(opt, ["help"]):
            init_args(pargs)
            if arg:
                pargs.show_help(argv)
            else:
                pargs.show_args()
            return
        elif pargs.is_matched(opt, ["chainid"]):
            print(arg)
            dataproof.configs.set_config("chain_id", arg)
            print(dataproof.configs.datas)
        elif pargs.is_matched(opt, ["info"]) :
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            logger.debug(f"arg_list:{arg_list}")
            show_workenv.run(arg_list)
        elif pargs.is_matched(opt, ["mod"]) :
            raise_with_check_conf()
            pargs.exit_check_opt_arg_min(opt, arg, 1)
            logger.debug(f"arg_list:{arg_list}")
            show_exec_args()
            violaslayer.run(arg_list)
            return
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
    logger.debug("end manage.main")

if __name__ == '__main__':
    main(len(sys.argv) - 1, sys.argv[1:])
