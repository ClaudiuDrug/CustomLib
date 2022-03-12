# -*- coding: UTF-8 -*-

import __main__
from collections import namedtuple
from os.path import dirname, realpath, join
from weakref import WeakValueDictionary

INSTANCES = WeakValueDictionary()

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])

# root directory
DIRECTORY: str = dirname(realpath(__main__.__file__))

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
        "handler": "file",  # or `console`
        "debug": False,
    },
}
