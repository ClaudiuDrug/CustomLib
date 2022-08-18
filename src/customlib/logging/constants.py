# -*- coding: UTF-8 -*-

from collections import namedtuple
from os.path import join
from threading import RLock
from weakref import WeakValueDictionary

from ..constants import ROOT

FOLDER: str = join(ROOT, "logs")

INSTANCES = WeakValueDictionary()

RECURSIVE_THREAD_LOCK = RLock()

ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])
FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])

BACKUP: dict = {
    "LOGGER": {
        "basename": "customlib",  # if handler is `file`
        "handler": "console",  # or `file`
        "debug": False,  # if set to `True` it will also print `DEBUG` messages
    }
}
