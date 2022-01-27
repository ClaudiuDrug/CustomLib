# -*- coding: UTF-8 -*-

from .cfgparser import CfgSingleton
from .constants import DEFAULTS, BACKUP
from .utils import get_path
from os.path import join

DEFAULTS.update({"directory": get_path()})
CONFIG: str = join(DEFAULTS.get("directory"), "config", "config.ini")

cfg = CfgSingleton()
cfg.set_defaults(**DEFAULTS)
cfg.read_dict(dictionary=BACKUP, source="<backup>")
