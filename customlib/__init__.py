# -*- coding: UTF-8 -*-

from configparser import ExtendedInterpolation

from .cfgparser import CfgParser
from .logging import Logger
from .utils import evaluate

CONVERTERS: dict = {
    "list": evaluate,
    "tuple": evaluate,
    "set": evaluate,
    "dict": evaluate,
}

cfg = CfgParser(
    interpolation=ExtendedInterpolation(),
    converters=CONVERTERS
)

log = Logger(config=cfg)
