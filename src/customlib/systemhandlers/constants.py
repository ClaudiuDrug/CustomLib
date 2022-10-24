# -*- coding: UTF-8 -*-

from platform import system

SYSTEM = system().upper()


class ES:
    CONTINUOUS: int = 0x80000000
    SYSTEM_REQUIRED: int = 0x00000001
    DISPLAY_REQUIRED: int = 0x00000002
