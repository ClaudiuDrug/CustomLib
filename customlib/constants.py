# -*- coding: UTF-8 -*-

from collections import namedtuple
from os.path import dirname, join
from sys import modules
from threading import RLock
from weakref import WeakValueDictionary

THREAD_LOCK = RLock()
INSTANCES = WeakValueDictionary()

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])

# root directory
DIRECTORY: str = dirname(modules["__main__"].__file__)

# default config file
CONFIG: str = join(DIRECTORY, "config", "config.ini")

# config default section
DEFAULTS: dict = {
    "directory": DIRECTORY,
}

# backup configuration
BACKUP: dict = {
    "FOLDERS": {
        "logger": r"${DEFAULT:directory}\logs"
    },
    "LOGGER": {
        "name": "customlib.log",
        "handler": "file",  # or "console"
        "debug": False,
    },
}
