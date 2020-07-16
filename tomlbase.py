#!/usr/bin/python3
import os, sys
#import setting
from comm import result
from comm.result import parse_except
from comm.functions import json_print
from comm.parseargs import parseargs
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tomlkit"))

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile
from pathlib import Path


class tomlbase():
    def __init__(self, tomlfile = None):
        self.__toml = None
        self.__content = None
        self._toml_file = ""
        self.__load_conf()

    def __load_conf(self):

        filename = self.__get_conf_file()
        if filename is None:
            self.is_loaded = False
            return 

        self._toml_file = filename 
        self.__toml = TOMLFile(filename)
        self.__content = self.toml.read()

        assert isinstance(self.__content, TOMLDocument)
        self.is_loaded = True
        for key, value in self.__content.items():
            setattr(self, key, value)

    def __get_conf_file(self):
        release_path = ""
        conffile = self.get_conf_env()
        #default toml. local or /etc/bvexchange
        if conffile is None:
            return None
        toml_file = conffile

        path = Path(toml_file)
        if not path.is_file() or not path.exists():
            raise Exception(f"not found toml file: {toml_file} in ({os.path.dirname(__file__)}  {release_path})")
        print(f"use config file: {toml_file}")
        return toml_file

    
    @property
    def is_loaded(self):
        return self.__is_loaded

    @is_loaded.setter
    def is_loaded(self, value):
        self.__is_loaded = value

    def __check_load_conf(self):
        if not self.is_loaded:
            self.__load_conf()

    def reset(self):
        self.__check_load_conf()
        if not self.is_loaded:
            print("not found configure file(toml).")
            sys.exit(-1)

    @property
    def toml_file(self):
        return self._toml_file

    @property
    def toml(self):
        return self.__toml

    @property
    def content(self):
        return self.__content

    def get(self, key):
        self.__check_load_conf()
        if not self.is_loaded:
            print("not found configure file(toml). use --conf ")
            sys.exit(-1)
        return self.content[key]

    @classmethod
    def set_conf_env(self, conffile):
        os.environ.setdefault("VIOLASLAYER_CONFIG", conffile)

    @classmethod
    def get_conf_env(self):
        return os.environ.get("VIOLASLAYER_CONFIG", None)

    @classmethod
    def set_conf_env_default(self):
        splits = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        basename = splits[-1]
        os.environ.setdefault("VIOLASLAYER_CONFIG", os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{basename}.toml"))

def main():
    tomlbase.set_conf_env_default()
    print(tomlbase.get_conf_env())
    pass



if __name__ == "__main__":
    main()
