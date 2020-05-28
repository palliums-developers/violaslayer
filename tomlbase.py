#!/usr/bin/python3
import os, sys
#import setting
from comm import result
from comm.result import parse_except
from comm.functions import json_print
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tomlkit"))

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile
from pathlib import Path


class tomlbase():
    def __init__(self, tomlfile):
        self.__toml_file = tomlfile

        filename = self.__get_conf_file(tomlfile)
        self.__toml = TOMLFile(filename)
        self.__content = self.toml.read()

        assert isinstance(self.content, TOMLDocument)

    def __get_conf_file(self, filename):
        name, ext = os.path.splitext(filename)
        if ext is None or ext.lower() != ".toml":
            raise Exception(f"{filename} is invalid.")

        release_path = f"/etc/{name}/"
        toml_file = os.path.join(os.path.dirname(__file__), filename)

        path = Path(toml_file)
        if not path.is_file() or not path.exists():
            toml_file = os.path.join(release_path, filename)
            path = Path(toml_file)
            if not path.is_file() or not path.exists():
                raise Exception(f"not found toml file: {filename} in ({os.path.dirname(__file__)}  {release_path})")
        print(f"use config file: {toml_file}")
        return toml_file


    @property
    def toml_file(self):
        return self._toml_file_

    @property
    def toml(self):
        return self.__toml

    @property
    def content(self):
        return self.__content

    def get(self, key):
        return self.content[key]

def main():
    pass



if __name__ == "__main__":
    main()
