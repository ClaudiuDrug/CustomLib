# -*- coding: UTF-8 -*-

from threading import RLock
from weakref import WeakValueDictionary


def dispatch_lock(name: str, container: WeakValueDictionary) -> RLock:
    if name not in container:
        # a strong reference is required
        instance = RLock()
        container[name] = instance
    return container[name]
