# -*- coding: UTF-8 -*-

from configparser import ConfigParser
from configparser import ExtendedInterpolation
from os.path import isfile
from sys import argv
from typing import Generator, Sequence

from .converters import CONVERTERS
from .exceptions import BadParameterError
from ..handles import FileHandle
from ..utils import ensure_folder


def new_config(**kwargs):
    """
    Create and return a new CfgParser instance.

    :param kwargs: It will be passed along to the CfgParser class.
    :return: A new CfgParser instance.
    """

    if "converters" in kwargs:
        CONVERTERS.update(kwargs.pop("converters"))
    _interpolation = kwargs.pop("interpolation", ExtendedInterpolation())

    parser = CfgParser(
        interpolation=_interpolation,
        converters=CONVERTERS,
        **kwargs
    )
    return parser


class ArgsParser(object):
    """`cmd-line` args parser."""

    def __init__(self):
        self.parameters = dict()

    def parse(self, args: Sequence[str]):
        args = (arg for arg in args)
        return self._parse(args)

    def _parse(self, args: Generator):
        for arg in args:
            if arg.startswith("--") is True:
                stripped = arg.strip("-")
                try:
                    section, option = stripped.split("-")
                except ValueError:
                    raise BadParameterError(f"Inconsistency in cmd-line parameters '{arg}'!")
                else:
                    try:
                        value = next(args)
                    except StopIteration:
                        raise BadParameterError(f"Missing value for parameter '{arg}'")
                    else:
                        if value.startswith("--") is False:
                            self._update(section, option, value)
                        else:
                            raise BadParameterError(f"Incorrect value '{value}' for parameter '{arg}'!")
            else:
                raise BadParameterError(f"Inconsistency in cmd-line parameters '{arg}'!")
        return self.parameters

    def _update(self, section: str, option: str, value: str):
        section = section.upper()
        if section not in self.parameters:
            self.parameters.update({section: {option: value}})
        else:
            section = self.parameters.get(section)
            section.update({option: value})


class CfgParser(ConfigParser):
    """Configuration handle."""

    def __init__(self, *args, **kwargs):
        super(CfgParser, self).__init__(*args, **kwargs)
        self._parser = ArgsParser()

    def parse(self, args: Sequence[str] = None):
        """Parse command-line arguments and update the configuration."""
        if args is None:
            args = argv[1:]

        if len(args) > 0:
            parameters = self._parser.parse(args)
            self.read_dict(dictionary=parameters, source="<cmd-line>")

    def set_defaults(self, **kwargs):
        """Update `DEFAULT` section using `kwargs`."""
        if len(kwargs) > 0:
            self._read_defaults(kwargs)

    def open(self, file_path: str, encoding: str = "UTF-8", fallback: dict = None):
        """
        Read from configuration `file_path`.
        If `file_path` does not exist and `fallback` is provided
        the latter will be used and a new configuration file will be written.
        """

        if isfile(file_path) is True:
            with FileHandle(file_path, "r", encoding=encoding) as file_handle:
                self.read_file(file_handle, source="<main>")

        elif fallback is not None:
            self.read_dict(dictionary=fallback, source="<backup>")
            self.save(file_path, encoding)

    def save(self, file_path: str, encoding: str):
        """Save the configuration to `file_path`."""
        ensure_folder(file_path)
        with FileHandle(file_path, "w", encoding=encoding) as file_handle:
            self.write(file_handle)
