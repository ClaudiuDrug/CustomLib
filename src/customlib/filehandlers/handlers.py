# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from os import fsync
from typing import IO

from .constants import RLOCK
from ..filelockers import FileLocker


class AbstractFileHandler(ABC):
    """Base abstract handler for all context-manager classes in this module."""

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs

    def __enter__(self):
        RLOCK.acquire()
        try:
            if not hasattr(self, "_handle"):
                self._handle = self.acquire(*self._args, **self._kwargs)
        except FileNotFoundError:
            RLOCK.release()
            raise
        else:
            return self._handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_handle"):
            self.release(self._handle)
            del self._handle
        RLOCK.release()

    def __delete__(self, instance):
        instance.release()

    @abstractmethod
    def acquire(self, *args, **kwargs) -> IO:
        raise NotImplementedError

    @abstractmethod
    def release(self, *args, **kwargs):
        raise NotImplementedError


class FileHandler(AbstractFileHandler):
    """Simple handler with thread & file lock management."""

    def __init__(self, *args, **kwargs):
        super(FileHandler, self).__init__(*args, **kwargs)
        self._file_lock = FileLocker()

    def acquire(self, *args, **kwargs):
        """Returns a new locked file handle."""
        RLOCK.acquire()
        try:
            handle = open(*args, **kwargs)
        except FileNotFoundError:
            raise
        else:
            self._file_lock.acquire(handle)
            return handle
        finally:
            RLOCK.release()

    def release(self, handle: IO):
        """Close the file handle and release the resources."""
        with RLOCK:
            handle.flush()
            if "r" not in handle.mode:
                fsync(handle.fileno())
            self._file_lock.release(handle)
            handle.close()
