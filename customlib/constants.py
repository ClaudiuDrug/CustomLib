# -*- coding: UTF-8 -*-

from collections import namedtuple
from os.path import dirname, realpath
from weakref import WeakValueDictionary

INSTANCES = WeakValueDictionary()

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])

DIRECTORY: str = dirname(dirname(realpath(__file__)))

DEFAULTS: dict = {
    "directory": DIRECTORY,
}

BACKUP: dict = {
    "FOLDERS": {
        "logger": r"${DEFAULT:directory}\logs"
    },
    "LOGGER": {
        "name": "custom-lib.log",
        "handler": "file",  # or `console`
        "debug": False,
    },
}
