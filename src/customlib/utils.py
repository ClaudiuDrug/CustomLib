# -*- coding: UTF-8 -*-

from os import makedirs
from os.path import dirname, isdir, realpath
from typing import Union


def del_prefix(target: str, prefix: str):
    """
    If `target` starts with the `prefix` string and `prefix` is not empty,
    return string[len(prefix):].
    Otherwise, return a copy of the original string.
    """
    if (len(prefix) > 0) and (target.startswith(prefix) is True):
        try:  # python >= 3.9
            return target.removeprefix(prefix)
        except AttributeError:  # python <= 3.7
            return target[len(prefix):]
    return target


def del_suffix(target: str, suffix: str):
    """
    If `target` ends with the `suffix` string and `suffix` is not empty,
    return string[:-len(suffix)].
    Otherwise, return a copy of the original string.
    """
    if (len(suffix) > 0) and (target.endswith(suffix) is True):
        try:  # python >= 3.9
            return target.removesuffix(suffix)
        except AttributeError:  # python <= 3.7
            return target[:-len(suffix)]
    return target


def encode(value: Union[str, bytes], encoding: str = "UTF-8") -> bytes:
    """Encode the string `value` with UTF-8."""
    if isinstance(value, str):
        return value.encode(encoding)
    return value


def decode(value: Union[bytes, str], encoding: str = "UTF-8") -> str:
    """Decode the bytes-like object `value` with UTF-8."""
    if isinstance(value, bytes):
        return value.decode(encoding)
    return value


def ensure_folder(path: str):
    """Read the file path and recursively create the folder structure if needed."""
    folder_path: str = dirname(realpath(path))
    make_dirs(folder_path)


def make_dirs(path: str):
    """Checks if a folder path exists and creates it if not."""
    if isdir(path) is False:
        makedirs(path)
