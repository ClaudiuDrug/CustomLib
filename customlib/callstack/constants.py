# -*- coding: UTF-8 -*-

from collections import namedtuple

FRAME = namedtuple("FRAME", ["file", "line", "code"])
TRACEBACK = namedtuple("TRACEBACK", ["file", "line", "code", "message"])
