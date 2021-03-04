#!/usr/bin/python3
import sys, getopt, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import setting as config_setting
import asyncio

_default_value = {}
class dataproof():
    ADDRS_SPLIT = ","
    FIELD_SPLIT = ":"

    def __init__(self):
        pass

    def set_default_value(self, key, value):
        _default_value.update({key:value})

    def get_default_value(self, key):
        return _default_value.get(key)

    def set_config(self, key, value):
        config_setting.setting.set(key, value)

    def get_config(self, key):
        default = self.get_default_value(key)
        return config_setting.setting.get(key, default)

    def default_values(self):
        return _default_value

    @property
    def datas(self):
        datas = {}
        datas.update(_default_value)
        datas.update(config_setting.setting.datas)
        return datas

class configdatas(dataproof):
    def __init__(self):
        dataproof.__init__(self)
        self.__init_default()

    def __del__(self):
        pass

    def __init_default(self):
        self.set_default_value("chain_id", 4)
        self.set_default_value("exchange_async", True)
        self.set_default_value("btc_client_loop", asyncio.get_event_loop())

    def __getattr__(self, name):
        print(f"{name}----")
        if name == "setting":
            return config_setting.setting

    def __call__(self, *args, **kwargs):
        key = args[0]
        return self.get_config(key)


class settingproxy(configdatas):
    def __init__(self):
        configdatas.__init__(self)

    def __getattr__(self, name):
        if name == "setting":
            return config_setting.setting

    def __call__(self, *args, **kwargs):
        key = args[0]
        return self.get_config(key)

configs = configdatas()
setting = settingproxy()

if __name__ == "__main__":
    setting.setting.set_conf_env("../violaslayer.toml")
    print(configs("violas_wallet"))
    print(setting.setting.get_conf_env())
