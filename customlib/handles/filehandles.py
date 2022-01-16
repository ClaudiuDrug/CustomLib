# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from os import fsync
from threading import RLock
from typing import IO

from ..locking import FileLock


class AbstractHandle(ABC):
    """Base abstract handle for all context-manager classes in this module."""

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        self._thread_lock = RLock()

    def __enter__(self):
        self._thread_lock.acquire()
        if hasattr(self, "_handle") is False:
            self._handle = self.acquire(*self._args, **self._kwargs)
        return self._handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_handle") is True:
            self.release(self._handle)
            del self._handle
        self._thread_lock.release()

    @abstractmethod
    def acquire(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def release(self, *args, **kwargs):
        raise NotImplementedError


class FileHandle(AbstractHandle):
    """Simple handle with thread lock and file lock management."""

    _file_lock = FileLock()

    @staticmethod
    def new(*args, **kwargs):
        """Returns a new file handle."""
        return open(*args, **kwargs)

    def acquire(self, *args, **kwargs):
        """Returns a new locked file handle."""
        with self._thread_lock:
            handle = self.new(*args, **kwargs)
            self._lock(handle)
            return handle

    def release(self, handle: IO):
        """Close the file handle and release the resources."""
        with self._thread_lock:
            handle.flush()
            if "r" not in handle.mode:
                fsync(handle.fileno())
            self._unlock(handle)
            handle.close()

    def _lock(self, handle: IO, flags: int = None):
        """Acquire a lock on the file handle."""
        if flags is None:
            flags = self._file_lock.get_flags(handle)
        self._file_lock.lock(handle, flags)

    def _unlock(self, handle: IO):
        """Unlock the file handle before closing it."""
        self._file_lock.unlock(handle)
