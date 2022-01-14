# -*- coding: UTF-8 -*-

from collections import namedtuple
from os.path import dirname, realpath
from weakref import WeakValueDictionary

DIRECTORY = dirname(dirname(realpath(__file__)))

ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])
FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])

INSTANCES = WeakValueDictionary()

DEFAULTS: dict = {
    "directory": DIRECTORY,
}

LOGGER: dict = {
    "FOLDERS": {
        "logger": r"${DEFAULT:directory}\logs"
    },
    "LOGGER": {
        "name": "customlib.log",
        "handler": "file",  # or `console`
        "debug": False,
    },
}
