# -*- coding: UTF-8 -*-


class RegistryKeyError(KeyError):
    """Exception raised for registry key errors."""


class DuplicateKeyError(RegistryKeyError):
    """Exception raised for duplicate registry keys."""


class MissingKeyError(RegistryKeyError):
    """Exception raised for missing registry keys."""
