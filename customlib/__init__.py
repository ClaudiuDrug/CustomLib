# -*- coding: UTF-8 -*-

from os.path import join

from .cfgparser import CfgSingleton
from .constants import DEFAULTS, BACKUP
from .logging import LogSingleton
from .utils import get_path

DEFAULTS.update({"directory": get_path()})
CONFIG: str = join(DEFAULTS.get("directory"), "config", "config.ini")

cfg = CfgSingleton()
cfg.set_defaults(**DEFAULTS)
cfg.read_dict(dictionary=BACKUP, source="<backup>")

log = LogSingleton()
