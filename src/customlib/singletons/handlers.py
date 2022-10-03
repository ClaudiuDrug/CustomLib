# -*- coding: UTF-8 -*-

from functools import wraps, update_wrapper

from .constants import INSTANCES


class MetaSingleton(type):
    """
    Singleton metaclass (for non-strict class).
    Restrict object to only one instance per runtime.
    """

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
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


class NamedSingleton(object):
    """
    Singleton decorator (for metaclass).
    With this class you have the option to create multiple instances by
    passing the `instance` parameter to a decorated class.
    Restrict object to only one instance per runtime.
    """

    def __init__(self, cls):
        update_wrapper(self, cls)
        self.cls = cls

    def __call__(self, *args, **kwargs):
        name: str = f"{kwargs.pop('instance', 'default')}.{self.cls.__name__}"

        if name not in INSTANCES:
            # a reference to the object is required.
            instance = self.cls(*args, **kwargs)
            INSTANCES[name] = instance

        return INSTANCES[name]
