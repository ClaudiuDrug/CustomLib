# -*- coding: UTF-8 -*-

from customlib import DEFAULTS, BACKUP, CONFIG
from customlib.cfgparser import CfgSingleton
from customlib.logging import LogSingleton

if __name__ == '__main__':

    # config
    cfg = CfgSingleton()  # one instance per runtime
    cfg.set_defaults(**DEFAULTS)
    cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)
    cfg.parse()  # we're parsing cmd-line arguments
    # cfg.parse(["--logger-debug", "True", "--logger-handler", "console"])

    log = LogSingleton()  # one instance per runtime
    log.debug("Testing debug messages...")  # by default debugging is set to False, must be enabled to work
    log.info("Testing info messages...")
    log.warning("Testing warning messages...")
    log.error("Testing error messages...")

    print(cfg.get("DEFAULT", "directory"))
