# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from atexit import register
from configparser import ExtendedInterpolation, NoSectionError, NoOptionError
from glob import glob
from os import walk
from os.path import join, exists, splitext
from shutil import rmtree
from sys import stdout
from threading import RLock
from typing import Union

from .callstack import info, get_level
from .cfgparser import CfgParser
from .constants import ROW, TRACEBACK, FRAME
from .handles import FileHandle
from .utils import timestamp, make_dirs, today, archive

_thread_lock = RLock()
cfg = CfgParser(interpolation=ExtendedInterpolation())


@register
def _cleanup():
    try:
        target = cfg.get("FOLDERS", "logger")
    except (NoSectionError, NoOptionError):
        pass
    else:
        folders = _scan(target)
        for folder, files in folders:
            archive(f"{folder}.zip", files)
            rmtree(folder)


def _scan(target: str):
    current_month = today().strftime("%B").lower()
    for root, folders, files in walk(target):
        if (root == target) or (len(folders) == 0):
            continue
        for folder in folders:
            if folder == current_month:
                continue
            folder = join(root, folder)
            files = join(folder, "*.log")
            yield folder, (file for file in glob(files))


def _set_cfg(instance: CfgParser):
    global cfg
    if instance is not None:
        cfg = instance


class Handler(ABC):
    """Base class for logging handlers."""

    @abstractmethod
    def emit(self, *args, **kwargs):
        raise NotImplementedError


class RowFactory(object):
    """`ROW` builder."""

    @staticmethod
    def join(message: str, frame: Union[TRACEBACK, FRAME]) -> str:
        """Attach traceback info to `message` if `frame` is an exception."""
        if isinstance(frame, TRACEBACK) is True:
            message = f"{message} Traceback: {frame.message}"
        return message

    def build(self, message: str, exception: Union[BaseException, tuple, bool]) -> ROW:
        """Construct and return a new ROW object."""
        frame = info(exception)
        return ROW(
            timestamp(),
            get_level(3),
            frame.file,
            frame.line,
            frame.code,
            self.join(message, frame)
        )


class StreamHandler(Handler):
    """Logging stream handler with thread lock management."""

    @staticmethod
    def _format(row: ROW):
        """Construct and return a string from the `row` object."""
        return f"[{row.time}] - {row.level} - <{row.file}, {row.line}, {row.code}>: {row.message}"

    def emit(self, record: ROW):
        """Acquire a thread lock and write the log record."""
        with _thread_lock:
            record = self._format(record)
            self.write(record)

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError


class FileHandler(StreamHandler):
    """File handler that writes log messages to disk."""

    @staticmethod
    def make_folder():
        _date = today()
        path = join(
            cfg.get("FOLDERS", "logger"),
            str(_date.year),
            _date.strftime("%B").lower(),
        )
        make_dirs(path)
        return path

    def __init__(self):
        self._file_path = None
        self._folder = None
        self._name = None
        self._ext = None
        self._idx = None
        self._size = 0

    def write(self, record: str):
        file_path = self.get_path()
        with FileHandle(file_path, "a", encoding="UTF-8") as file_handle:
            file_handle.write(f"{record}\n")
            self._size = file_handle.tell()

    def get_path(self):
        if self._file_path is None:
            self._file_path = self.make_path()
        else:
            self.check_size()
        return self._file_path

    def make_path(self):
        file_path = join(self.get_folder(), self.get_name())
        if exists(file_path) is True:
            return self.make_path()
        return file_path

    def get_folder(self):
        if self._folder is None:
            self._folder = self.make_folder()
        return self._folder

    def get_name(self):
        if (self._name is None) and (self._ext is None):
            self._name, self._ext = splitext(cfg.get("LOGGER", "name", fallback="customlib.log"))
        return f"{today()}_{self._name}.{self.get_idx()}.{self._ext.strip('.')}"

    def get_idx(self):
        if self._idx is None:
            self._idx = 0
        else:
            self._idx += 1
        return self._idx

    def check_size(self):
        if self._size >= ((1024 * 1024) - 1024):
            self._file_path = self.make_path()


class StdHandler(StreamHandler):
    """Simple `stdout` handler."""

    @staticmethod
    def write(record: str):
        """Write the log record to console and flush the handle."""
        stdout.write(f"{record}\n")
        stdout.flush()


class BaseLogger(Handler):
    """Base logging handler."""

    _handlers: dict = {
        "console": StdHandler,
        "file": FileHandler,
    }

    def __init__(self, config: CfgParser = None):
        _set_cfg(config)
        self._stream_handler = None
        self._row_factory = RowFactory()

    def get_stream(self, target: str):
        handler = self._handlers.get(target)
        return handler()

    def set_stream(self, handler: Union[StdHandler, FileHandler]):
        """Set the handler to output log messages."""
        self._stream_handler = handler

    def emit(self, message: str, exception: Union[BaseException, tuple, bool]):
        """Construct the row object and emit using the stream handler."""

        if self._stream_handler is None:
            self._stream_handler = self.get_stream(cfg.get("LOGGER", "handler", fallback="console"))

        with _thread_lock:
            row = self._row_factory.build(message, exception)
            self._stream_handler.emit(row)


class Logger(BaseLogger):
    """Main logging handler."""

    def debug(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `DEBUG`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        if cfg.getboolean("LOGGER", "debug", fallback=False) is True:
            self.emit(message=message, exception=exception)

    def info(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `INFO`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def warning(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `WARNING`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def error(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `ERROR`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)
