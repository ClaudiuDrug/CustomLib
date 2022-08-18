# -*- coding: UTF-8 -*-

from os.path import dirname, realpath
from sys import modules
from types import ModuleType

MODULE: ModuleType = modules.get("__main__")
ROOT: str = dirname(realpath(MODULE.__file__))
