# -*- coding: UTF-8 -*-

from ast import literal_eval


def evaluate(value: str):
    """Transform a string to an appropriate data type."""
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    return value


CONVERTERS = {
    "list": evaluate,
    "tuple": evaluate,
    "set": evaluate,
    "dict": evaluate,
}
