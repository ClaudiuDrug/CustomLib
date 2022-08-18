# -*- coding: UTF-8 -*-

from decimal import Decimal
from re import compile
from typing import Any, Union, List, Match

from ..utils import encode, decode


def single_quote(value: Any) -> Any:
    """Apply quote to value if is instance of string."""
    if isinstance(value, str):
        return f"'{value}'"
    return value


def clean_string(target: str, text: str) -> str:
    """Search for `target` in `text` and remove it."""
    results = find_substring(target, text)

    if results is not None:
        start, end = results
        space = start - 1
        comma = space - 1

        if text[comma:space] == ",":
            return text.replace(text[comma:end], "")
        elif text[space:start] == " ":
            return text.replace(text[space:end], "")
        else:
            return text.replace(text[start:end], "")

    return text.strip(" ")


def find_substring(target: str, text: str) -> tuple:
    result = text.find(target)

    if result != -1:
        return result, result + len(target)


def find_in_file(file_path: str, target_name: str, pattern: str) -> List[str]:
    """Search for a given pattern in file."""
    group: str = re_group(target_name, pattern)

    with open(file_path, "r", encoding="UTF-8") as fh:
        text: str = fh.read()
        matches = re_search(text, group)

        if len(matches) > 0:
            return [item.group(target_name) for item in matches]


def re_search(text: str, pattern: str) -> List[Match[str]]:
    """Search for a given pattern and return a list of results."""
    template = compile(pattern)
    return [item for item in template.finditer(text)]


def re_group(name: str, pattern: str) -> str:
    """Regex search groups."""
    return fr"(?P<{name}>{pattern})"


def to_bytes(value: Union[Decimal, bytes], encoding: str = "UTF-8") -> bytes:
    """From decimal to bytes."""
    if isinstance(value, Decimal):
        return encode(str(value), encoding)
    return value


def to_decimal(value: Union[bytes, Decimal], encoding: str = "UTF-8") -> Decimal:
    """From bytes to decimal."""
    if isinstance(value, bytes):
        return Decimal(decode(value, encoding))
    return value
