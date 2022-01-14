# -*- coding: UTF-8 -*-

from os.path import dirname, realpath, join
from sys import exit as sys_exit
from uuid import uuid1

from customlib import CfgParser
from customlib import Logger
from customlib import Cypher
from customlib import FileHandle

if __name__ == '__main__':

    DIRECTORY = dirname(realpath(__file__))
    CONFIG = join(DIRECTORY, "config", "config.ini")

    DEFAULTS: dict = {
        "directory": DIRECTORY,
    }

    BACKUP: dict = {
        "FOLDERS": {
            "logger": r"${DEFAULT:directory}\logs"
        },
        "LOGGER": {
            "name": "customlib.log",
            "handler": "file",  # or `console`
            "debug": False,
        },
    }

    cfg = CfgParser()
    cfg.set_defaults(**DEFAULTS)
    cfg.open(CONFIG, fallback=BACKUP)
    cfg.parse()

    # log = Logger(config=cfg)

    # or

    log = Logger()
    log.set_settings(config=cfg)

    log.debug("testing debug messages...")
    log.info("testing info messages...")
    log.warning("testing warning messages...")
    log.error("testing error messages...")

    with FileHandle("file_1.txt", "a", encoding="UTF-8") as file_1:
        file_1.write("Handler 1 writing this line...\n")

    with FileHandle("file_1.txt", "a", encoding="UTF-8") as file_2:
        file_2.write("Handler 2 writing this line...\n")

    cypher = Cypher()
    cypher.password(value="fghj-6d5x", salt="p+CU4HPDoL>TDUga")

    encrypted = cypher.encrypt("This is a hidden message!")
    print("encrypted:", encrypted)

    decrypted = cypher.decrypt(encrypted)
    print("decrypted:", decrypted)

    decrypted = cypher.decrypt(
        "gAAAAABh3gt2UE68zxY-1HAvidlLNqHCrp5DEv7Ai-NOVg47dm2S"
        "AO2CFmI77R-NbLfSykgBqaeoTkAdGA7qDEmngzqXt4UKZjbzSR0cLDS0aaXV1SkTo44="
    )
    print("decrypted:", decrypted)

    print(uuid1())

    sys_exit(0)
