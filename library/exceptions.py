# -*- coding: UTF-8 -*-

# KeyVault exceptions
class BaseVaultError(Exception):
    """Base exception class for backends module."""


class PasswordGetError(BaseVaultError):
    """Exception for password getter."""


class KeyEncryptionError(BaseVaultError):
    """Exception for password encryption error."""


class KeyDecryptionError(BaseVaultError):
    """Exception for password encryption error."""


# File locker exceptions
class BaseLockException(Exception):
    """Base exception class."""

    # Error codes:
    LOCK_FAILED = 1

    def __init__(self, *args, **kwargs):
        self.handle = kwargs.pop("handle")
        super(BaseLockException, self).__init__(*args)


class LockException(BaseLockException):
    """Lock exception."""


# CfgParser exceptions
class BadParameterError(Exception):
    """Exception class used to signal bad configuration."""
