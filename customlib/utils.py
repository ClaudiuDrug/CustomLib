# -*- coding: UTF-8 -*-

from ast import literal_eval
from datetime import datetime, timezone, date
from functools import wraps
from os import makedirs, getenv
from os.path import dirname, realpath, isdir
from typing import Union

from .constants import INSTANCES


class MetaSingleton(type):
    """
    Singleton metaclass (for non-strict class).
    Restrict object to only one instance per runtime.
    """

    def __call__(cls, *args, **kwargs):
        if hasattr(cls, "_instance") is False:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instance


def singleton(cls):
    """
    Singleton decorator (for metaclass).
    Restrict object to only one instance per runtime.
    """

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in INSTANCES:
            # a strong reference to the object is required.
            instance = cls(*args, **kwargs)
            INSTANCES[cls] = instance
        return INSTANCES[cls]
    return wrapper


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


def get_posix():
    """POSIX timestamp as float. Number of seconds since Unix Epoch in UTC."""
    utc = get_utc()
    return utc.timestamp()


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


def evaluate(value: str):
    """Transform a string to an appropriate data type."""
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    return value


def get_path() -> str:
    """Get the root directory of the project."""
    return getenv("PYTHONPATH").split(";")[0]
