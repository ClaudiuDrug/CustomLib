# -*- coding: UTF-8 -*-

class BaseLockException(Exception):
    """Base exception class."""

    # Error codes:
    LOCK_FAILED = 1

    def __init__(self, *args, **kwargs):
        self.handle = kwargs.pop("handle")
        super(BaseLockException, self).__init__(*args)


class LockException(BaseLockException):
    """Lock exception."""
