# -*- coding: UTF-8 -*-

from __future__ import annotations

from typing import Generator

from .collections import Tables, Columns, Indexes, Views, Triggers
from .dialect import DDL, DML, DQL, Comparison
from .engine import SQLite
from .exceptions import SQLiteIndexError, MissingColumnsError
from .utils import single_quote


class Model(object):
    """Base ORM model."""

    @staticmethod
    def _filter(target: str, *args, **kwargs) -> Generator:
        """
        Find items with attr `typename` and yield only those that match
        `target`.
        """
        target: str = target.lower()  # force lowercase
        items: tuple = args + tuple(kwargs.values())

        for item in items:

            if hasattr(item, "typename"):
                if item.typename == target:
                    yield item

    def __init__(self, name: str):
        self.name = name

    @property
    def typename(self):
        return self.__class__.__name__.lower()

    @property
    def parent(self) -> Model:
        return getattr(self, "_parent", None)

    @parent.setter
    def parent(self, value: Model):
        setattr(self, "_parent", value)

    def _add_child(self, item: Model):
        if item.parent is None:
            item.parent = self


class Schema(Model, DDL):
    """SQLite schema ORM model."""

    def __init__(self, name: str = "main", **kwargs):
        super(Schema, self).__init__(name=name)

        self.engine = kwargs.pop("engine", None)
        self.tables: Tables = Tables()
        self.indexes: Indexes = Indexes()

        # ************* not implemented: ************* #

        self.views: Views = Views()
        self.triggers: Triggers = Triggers()

        # ******************************************** #

    def add_table(self, item: Table):
        self._add_child(item)
        self.tables.insert({item.name: item})

    def add_index(self, item: Index):
        self._add_child(item)
        self.indexes.insert({item.name: item})

    # ************* not implemented: ************* #

    # def add_view(self, view: View):
    #     self._add_child(view)
    #     self.views.insert({view.name: view})

    # def add_trigger(self, trigger: Trigger):
    #     self._add_child(trigger)
    #     self.triggers.insert({trigger.name: trigger})

    # ******************************************** #

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"engine={self.engine}",
            f"tables={self.tables or None}",
            f"indexes={self.indexes or None}",
            f"views={self.views or None}",
            f"triggers={self.triggers or None}",
        )
        return f"{typename}({', '.join(fields)})"


class Table(Model, DDL, DML, DQL):
    """SQLite table ORM model."""

    @staticmethod
    def _find_autoincrement(columns: Columns) -> Column:
        for key, value in columns.items():
            if value.autoincrement is True:
                return value

    def __init__(self, name: str, schema: Schema, *args, **kwargs):
        super(Table, self).__init__(name=name)

        self.schema = schema
        self.temp: bool = kwargs.pop("temp", False)

        self.c = self.columns = Columns()
        self.i = self.indexes = self.schema.indexes

        self._map_columns(*args, **kwargs)
        self._map_indexes(*args, **kwargs)

        self.schema.add_table(self)

    @property
    def engine(self) -> SQLite:
        return self.schema.engine

    @engine.setter
    def engine(self, value: SQLite):
        self.schema.engine = value

    def add_column(self, item: Column):
        self._add_child(item)
        self.columns.insert({item.name: item})

    def _map_columns(self, *args, **kwargs):
        for column in self._filter("column", *args, **kwargs):
            self.add_column(column)

        if len(self.columns) == 0:
            raise MissingColumnsError(f"Cannot create table '{self.name}' without any column!")

        self._resolve_constraints(self.columns)

    def _resolve_constraints(self, columns: Columns):
        autoincrement: Column = self._find_autoincrement(columns)

        if autoincrement is not None:

            for key, value in columns.items():
                if value is autoincrement:
                    continue
                else:
                    value.autoincrement = value.primary = False

    def _map_indexes(self, *args, **kwargs):
        for index in self._filter_indexed(self.columns):
            self.schema.add_index(index)

        for index in self._filter("index", *args, **kwargs):

            for column in index.columns:

                if column.name not in self.columns:
                    raise SQLiteIndexError(
                        f"{self.typename.title()} '{self.name}' has no such column '{column.name}'!"
                    )

                if column.type.upper() == "DUMMY":
                    column = self.columns.get(column.name)
                    index.columns.update({column.name: column})

            if index.table is not None:

                # can table be a string? we'll see...
                if index.table.name != self.name:
                    raise SQLiteIndexError(f"Wrong table name '{index.table.name}' for this index '{index.name}'!")
            else:
                index.table = self

            self.schema.add_index(index)

    def _filter_indexed(self, columns: Columns) -> Generator:
        for key, value in columns.items():

            if value.index is True:
                index = Index(
                    self._idx_name(key, value.unique),
                    value,
                    table=self,
                    unique=value.unique,

                )
                self._add_child(index)
                yield index

    def _idx_name(self, basename: str, unique: bool) -> str:
        if unique is True:
            return f"ux_{basename}_{self.name}"
        return f"ix_{basename}_{self.name}"

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"schema='{self.schema.name}'",
            f"columns={self.columns}",
        )
        return f"{typename}({', '.join(fields)})"


# noinspection PyShadowingBuiltins
class Column(Model):
    """SQLite column ORM model."""

    def __init__(self, name: str, type: str, **kwargs):
        super(Column, self).__init__(name=name)

        self.type: str = type
        self.null: bool = kwargs.pop("null", True)
        self.primary: bool = kwargs.pop("primary", False)
        self.autoincrement: bool = kwargs.pop("autoincrement", False)
        self.foreign: bool = kwargs.pop("foreign", False)
        self.references: Column = kwargs.pop("references", None)
        self.unique: bool = kwargs.pop("unique", False)
        self.index: bool = kwargs.pop("index", False)

        self._rezolve_constraints()

    def __call__(self, alias: str):
        self.alias = alias
        return self

    def __eq__(self, other):
        return Comparison(name=self.name, operator="==", value=other)

    def __ne__(self, other):
        return Comparison(name=self.name, operator="!=", value=other)

    def __le__(self, other):
        return Comparison(name=self.name, operator="<=", value=other)

    def __ge__(self, other):
        return Comparison(name=self.name, operator=">=", value=other)

    def __lt__(self, other):
        return Comparison(name=self.name, operator="<", value=other)

    def __gt__(self, other):
        return Comparison(name=self.name, operator=">", value=other)

    def is_null(self):
        return Comparison(name=self.name, operator="IS", value="NULL")

    def is_not_null(self):
        return Comparison(name=self.name, operator="IS NOT", value="NULL")

    def like(self, value: str):
        return Comparison(name=self.name, operator="LIKE", value=value)

    def _rezolve_constraints(self):

        if self.foreign is True:
            self.primary = self.autoincrement = False

        if self.autoincrement is True:
            self.primary = True

    def __repr__(self) -> str:
        typename: str = self.typename.title()
        fields: tuple = tuple(
            f"{key}={single_quote(value)}"
            for key, value in self.__dict__.items()
            if (key.startswith("_") is False)
        )
        return f"{typename}({', '.join(fields)})"


class Index(Model, DDL):
    """SQLite `INDEX` ORM model."""

    @staticmethod
    def _filter(target: str, *args, **kwargs) -> Generator:
        """
        Filter and return `Column` objects.

        If item is a string instance it will be converted to a `Column` object.
        """
        target: str = target.lower()  # force lowercase
        items: tuple = args + tuple(kwargs.values())

        for item in items:

            if hasattr(item, "typename"):
                if item.typename == target:
                    yield item

            elif isinstance(item, str):
                yield Column(name=item, type="DUMMY")

    def __init__(self, name: str, *args, **kwargs):
        super(Index, self).__init__(name=name)

        self.table: Table = kwargs.pop("table", None)
        self.unique: bool = kwargs.pop("unique", False)
        self.c = self.columns = Columns()

        self._map_columns(*args, **kwargs)

    @property
    def engine(self) -> SQLite:
        return self.table.engine

    @engine.setter
    def engine(self, value: SQLite):
        self.table.engine = value

    def _map_columns(self, *args, **kwargs):
        for column in self._filter("column", *args, **kwargs):
            self.columns.insert({column.name: column})

        if len(self.columns) == 0:
            raise MissingColumnsError(f"Cannot create index '{self.name}' without any column!")

    def __repr__(self):
        typename: str = self.typename.title()
        fields: tuple = (
            f"name='{self.name}'",
            f"table='{self.table.name}'",
            f"columns={tuple(column.name for column in self.columns)}",
            f"unique={self.unique}",
        )
        return f"{typename}({', '.join(fields)})"
