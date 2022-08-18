# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from atexit import register
from dataclasses import dataclass, field, asdict
from datetime import date
from glob import glob
from os import makedirs, walk
from os.path import join, exists
from shutil import rmtree
from sys import stdout
from typing import Union, Any, Generator

from .constants import RECURSIVE_THREAD_LOCK, BACKUP, FOLDER, TRACEBACK, FRAME, ROW
from .utils import get_timestamp, get_level, get_caller, get_traceback, archive
from ..config import get_config, CfgParser
from ..constants import ROOT
from ..filehandlers import FileHandler

cfg: CfgParser = get_config(name=f"logging.defaults")
cfg.set_defaults(directory=ROOT)
cfg.read_dict(dictionary=BACKUP, source="<logging>")


class AbstractHandler(ABC):
    """Base handler for all classes in this module."""

    def __init__(self, **kwargs):
        if ("config" in kwargs) and (kwargs.get("config") is not None):
            self.cfg: CfgParser = kwargs.pop("config")

    @property
    def cfg(self) -> CfgParser:
        return getattr(self, "_cfg", cfg)

    @cfg.setter
    def cfg(self, value: CfgParser):
        setattr(self, "_cfg", value)


class AbstractLogHandler(AbstractHandler):
    """Base handler for all classes in this module."""

    @abstractmethod
    def emit(self, *args, **kwargs):
        raise NotImplementedError


class OutputHandler(AbstractLogHandler):
    """Base abstract handler for all classes in this module."""

    def emit(self, message: str):
        self.write(message)

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError


class AbstractLogFactory(AbstractHandler):
    """Base abstract handler for all classes in this module."""

    @abstractmethod
    def build(self, *args, **kwargs):
        raise NotImplementedError


class RowFactory(AbstractLogFactory):

    @staticmethod
    def _get_info(exception: Union[BaseException, tuple, bool]) -> Union[TRACEBACK, FRAME]:
        """
        Get information about the most recent exception caught by an except clause
        in the current stack frame or in an older stack frame.
        """
        if exception is not None:
            try:
                return get_traceback(exception)
            except AttributeError:
                pass

        return get_caller(5)

    @staticmethod
    def _attach_info(message: str, frame: Union[TRACEBACK, FRAME]) -> str:
        """Attach traceback info to `message` if `frame` is an exception."""
        if isinstance(frame, TRACEBACK) is True:
            message = f"{message} Traceback: {frame.message}"
        return message

    def build(self, message: str, exception: Union[BaseException, tuple, bool]) -> ROW:
        frame = self._get_info(exception)
        return ROW(
            time=get_timestamp(fmt="%Y-%m-%d %H:%M:%S.%f"),
            level=get_level(3),
            file=frame.file,
            line=frame.line,
            code=frame.code,
            message=self._attach_info(message, frame),
        )


class FormatFactory(AbstractLogFactory):

    @staticmethod
    def _format(row: ROW) -> str:
        """Construct and return a string from the `row` object."""
        return f"[{row.time}] - {row.level} - <{row.file}, {row.line}, {row.code}>: {row.message}"

    def build(self, row: ROW) -> str:
        """Construct and return a new ROW object."""
        return self._format(row)


class StdStream(OutputHandler):
    """Handler used for logging to console."""

    @staticmethod
    def write(record: str):
        """Write the log record to console and flush the handle."""
        stdout.write(f"{record}\n")
        stdout.flush()


class NoStream(OutputHandler):
    """Handler used for... well... nothing."""

    @staticmethod
    def write(record: str):
        """Do nothing for when you actually need it."""
        pass


class FileStream(OutputHandler):
    """Handler used for logging to a file."""

    def __init__(self, **kwargs):
        super(FileStream, self).__init__(**kwargs)

        self._file_path = None
        self._folder_path = None
        self._file_name = None

        self._file_idx: int = 0
        self._file_size: int = 0

    def write(self, record: str):
        file_path = self.get_file_path()
        with FileHandler(file_path, "a", encoding="UTF-8") as fh:
            fh.write(f"{record}\n")
            self._file_size = fh.tell()

    def get_file_path(self):

        if self._file_path is None:
            self._file_path: str = self._get_file_path()

        elif self._file_size >= ((1024 * 1024) - 1024):
            self._file_path: str = self._get_file_path()

        return self._file_path

    def _get_file_path(self):
        file_path = join(self.get_folder_path(), self.get_file_name())

        if exists(file_path) is True:
            return self._get_file_path()

        return file_path

    def get_folder_path(self):
        if self._folder_path is None:
            self._folder_path = self._get_folder_path()

        if not exists(self._folder_path):
            makedirs(self._folder_path)

        return self._folder_path

    def get_file_name(self):
        return f"{date.today()}_{self.cfg.get('LOGGER', 'basename')}.{self.get_file_idx()}.log"

    def get_file_idx(self):
        self._file_idx += 1
        return self._file_idx

    def _get_folder_path(self) -> str:
        root: str = self.cfg.get("LOGGER", "folder", fallback=FOLDER)
        today: date = date.today()
        return join(root, str(today.year), today.strftime("%B").lower())


@dataclass
class Handlers(object):

    config: CfgParser = field(default=None, repr=False)

    console: StdStream = field(default_factory=StdStream)
    nostream: NoStream = field(default_factory=NoStream)
    file: FileStream = field(default_factory=FileStream)

    def __post_init__(self):
        self._handlers: dict = asdict(self)
        self._set_config(self.config)

    def _set_config(self, value: CfgParser):
        if value is not None:
            for handler in self._handlers.values():
                handler.cfg = value

    def get(self, target: str) -> Any:
        return self._handlers.get(target)


class StreamHandler(AbstractLogHandler):

    def __init__(self, **kwargs):
        super(StreamHandler, self).__init__(**kwargs)
        self._handlers: Handlers = Handlers(config=self.cfg)

    @property
    def handler(self) -> OutputHandler:
        return self._handlers.get(
            target=self.cfg.get("LOGGER", "handler")
        )

    def emit(self, message: str):
        self.handler.emit(message)


class BaseLogger(AbstractLogHandler):
    """Base logging handler."""

    @staticmethod
    def _months_list(today: date):
        return [
            date(today.year, n, 1).strftime("%B").lower()
            for n in range(1, 13)
            if n != today.month
        ]

    def __init__(self, **kwargs):
        super(BaseLogger, self).__init__()
        self.set_config(**kwargs)

        self._factory = RowFactory()
        self._format = FormatFactory()
        self._stream = StreamHandler(config=self.cfg)

        register(self.cleanup)

    def set_config(self, **kwargs):

        if len(kwargs) > 0:
            self._set_config(**kwargs)

    def _set_config(self, **kwargs):

        if "config" in kwargs:
            self.cfg: Union[CfgParser, str] = kwargs.pop("config")

            if isinstance(self.cfg, str):
                self.cfg: CfgParser = get_config(name=self.cfg)

        else:
            options: dict = BACKUP.get("LOGGER").copy()
            options.update(**kwargs)

            if self.cfg is cfg:
                self.cfg: CfgParser = get_config(name=self)

            self.cfg.read_dict(dictionary={"LOGGER": options}, source="<logging>")

    def cleanup(self):
        root: str = self.cfg.get("LOGGER", "folder", fallback=FOLDER)

        if exists(root):

            folders = self._scan(root)

            for folder, files in folders:
                archive(f"{folder}.zip", files)
                rmtree(folder)

    def _scan(self, target: str) -> Generator:
        today: date = date.today()
        month: str = today.strftime("%B").lower()
        months: list = self._months_list(today)

        for root, folders, files in walk(target):

            if (root == target) or (len(folders) == 0):
                continue

            for folder in folders:
                if folder == month:
                    continue

                if folder in months:

                    folder: str = join(root, folder)
                    files: str = join(folder, "*.log")

                    yield folder, (file for file in glob(files))

    def emit(self, message: str, exception: Union[BaseException, tuple, bool]):
        with RECURSIVE_THREAD_LOCK:
            row = self._factory.build(message, exception)
            message = self._format.build(row)
            self._stream.emit(message)


class Logger(BaseLogger):
    """Logging class with thread and file lock ability."""

    def debug(self, message: str, exception: Union[BaseException, tuple, bool] = False):
        """
        Log a message with level `DEBUG`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        if self.cfg.getboolean("LOGGER", "debug") is True:
            self.emit(message=message, exception=exception)

    def info(self, message: str, exception: Union[BaseException, tuple, bool] = False):
        """
        Log a message with level `INFO`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def warning(self, message: str, exception: Union[BaseException, tuple, bool] = False):
        """
        Log a message with level `WARNING`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def error(self, message: str, exception: Union[BaseException, tuple, bool] = False):
        """
        Log a message with level `ERROR`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def critical(self, message: str, exception: Union[BaseException, tuple, bool] = False):
        """
        Log a message with level `CRITICAL`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)
