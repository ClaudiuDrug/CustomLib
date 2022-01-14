# -*- coding: UTF-8 -*-

from collections import namedtuple
from weakref import WeakValueDictionary

ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])
FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])

INSTANCES = WeakValueDictionary()
