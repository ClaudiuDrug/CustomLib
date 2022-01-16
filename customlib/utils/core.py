# -*- coding: UTF-8 -*-

from datetime import datetime, timezone, date
from os import makedirs
from os.path import dirname, realpath, isdir
from typing import Union


def today():
    """Return current date a `datetime.date` object."""
    return date.today()


def timestamp(fmt: str = "%Y-%m-%d %H:%M:%S.%f") -> str:
    """:returns: an aware localized and formatted `datetime` string object."""
    local = get_local()
    return local.strftime(fmt)


def get_local() -> datetime:
    """:returns: an aware localized datetime object."""
    utc = get_utc()
    return utc.astimezone()


def get_utc() -> datetime:
    """:returns: an UTC `datetime` object."""
    return datetime.now(timezone.utc)


def ensure_folder(path: str):
    """Read the file path and recursively create the folder structure if needed."""
    folder_path: str = dirname(realpath(path))
    make_dirs(folder_path)


def make_dirs(path: str):
    """Checks if a folder path exists and creates it if not."""
    if isdir(path) is False:
        makedirs(path)


def encode(value: Union[str, bytes]) -> bytes:
    """Encode the string `value` with UTF-8."""
    if isinstance(value, str) is True:
        value = value.encode("UTF-8")
    return value


def decode(value: Union[bytes, str]) -> str:
    """Decode the bytes-like object `value` with UTF-8."""
    if isinstance(value, bytes) is True:
        value = value.decode("UTF-8")
    return value
