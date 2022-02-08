# -*- coding: UTF-8 -*-

from collections import namedtuple
from weakref import WeakValueDictionary

INSTANCES = WeakValueDictionary()

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
ROW = namedtuple("ROW", ["time", "level", "file", "line", "code", "message"])
