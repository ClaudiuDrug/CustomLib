# -*- coding: UTF-8 -*-

from threading import Thread
from time import sleep

from customlib.config import cfg
from customlib.constants import CONFIG, DEFAULTS, BACKUP
from customlib.handles import FileHandle
from customlib.logging import log


class TestClass(object):
    """testing class"""

    def logger_test(self):
        log.info("Test started.")
        try:
            # By default debugging is set to `False`, must be enabled to work!
            log.debug("Trying to divide by zero...")
            x = 123 / 0
        except ZeroDivisionError as div_error:
            log.error("Oups! Dividing by zero is not a thing in this universe...", exception=div_error)  # or `True`
        else:
            log.warning("That actually worked? Something ain't right!")
        log.info("Test finished!")


def logger_test():
    log.info("Test started.")
    try:
        # By default debugging is set to `False`, must be enabled to work!
        log.debug("Trying to divide by zero...")
        x = 123 / 0
    except ZeroDivisionError as div_error:
        log.error("Oups! Dividing by zero is not a thing in this universe...", exception=div_error)  # or `True`
    else:
        log.warning("That actually worked? Something ain't right!")
    log.info("Test finished!")


def file_handle_test(file_path: str, message: str):
    with FileHandle(file_path, "a", encoding="UTF-8") as fh:
        print(message)
        sleep(5)
        fh.write(f"{message}\n")


if __name__ == '__main__':

    # config
    cfg.set_defaults(**DEFAULTS)
    cfg.open(file_path=CONFIG, encoding="UTF-8", fallback=BACKUP)

    # we're parsing cmd-line arguments
    # cfg.parse()

    # we can also do this...
    cfg.parse(["--logger-debug", "True", "--logger-handler", "console"])
    # cfg.parse(["--logger-debug", "True", "--logger-handler", "file"])

    log.debug("Testing debug messages...")  # by default debugging is set to False, must be enabled to work
    log.info("Testing info messages...")
    log.warning("Testing warning messages...")
    log.error("Testing error messages...")

    TestClass().logger_test()

    threads = list()

    for name in ["THREAD 1", "THREAD 2", "THREAD 3"]:
        thread = Thread(
            target=file_handle_test,
            name=name,
            kwargs={
                "file_path": "test_file.txt",
                "message": f"{name} is in control now...",
            },
            daemon=True,
        )
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    for x in range(20000):
        log.info(f"{x} testing info messages...")