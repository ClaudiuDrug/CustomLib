# -*- coding: UTF-8 -*-

from os import getcwd
from os.path import join

from customlib import cfg
from customlib import log

if __name__ == '__main__':

    DIRECTORY: str = getcwd()
    CONFIG: str = join(DIRECTORY, "config", "config.ini")
    DEFAULTS: dict = {"directory": DIRECTORY}
    BACKUP: dict = {
        "FOLDERS": {
            "logger": r"${DEFAULT:directory}\logs"
        },
        "LOGGER": {
            "name": "custom-lib.log",
            "handler": "file",  # or `console`
            "debug": False,
        },
    }

    # config
    cfg.set_defaults(**DEFAULTS)
    cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)

    # we're parsing cmd-line arguments
    cfg.parse()

    # we can also do this...
    # cfg.parse(["--logger-debug", "True", "--logger-handler", "console"])

    log.debug("Testing debug messages...")  # by default debugging is set to False, must be enabled to work
    log.info("Testing info messages...")
    log.warning("Testing warning messages...")
    log.error("Testing error messages...")
