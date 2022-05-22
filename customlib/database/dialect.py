# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from collections import namedtuple
from string import Template
from types import SimpleNamespace
from typing import Any

from ..exceptions import ArgumentError, SqlExecutionError

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
TEMPLATES = SimpleNamespace(
    index=SimpleNamespace(
        create=Template('CREATE ${unique} INDEX ${if_not_exists} "${name}" ON "${table}" ("${column}")'),
        drop=Template('DROP INDEX ${if_exists} "${name}"'),
    ),
    column=SimpleNamespace(
        clause=Template('"${name}" ${type} ${null} ${unique}'),
        comparison=Template("${column} ${operator} ${value}"),
    ),
    table=SimpleNamespace(
        create=Template('CREATE TABLE ${if_not_exists} "${table}" (${columns})'),
        drop=Template('DROP TABLE ${if_exists} "${table}"'),
        insert=Template('INSERT INTO "${table}" (${columns}) VALUES (${values})'),
        update=Template('UPDATE "${table}" ${set} ${where}'),
        delete=Template('DELETE FROM "${table}" ${where}'),
        select=Template('SELECT ${columns} FROM "${table}" ${where}'),
    ),
)

COMPARISON = namedtuple("COMPARISON", ["column", "operator", "value"])


class Statement(ABC):
    """Base SQL statement constructor."""

    @staticmethod
    def _clean(stmt: str):
        placeholders = {
            "${if_not_exists}",
            "${if_exists}",
            "${columns}",
            "${column}",
            "${operator}",
            "${values}",
            "${value}",
            "${set}",
            "${where}",
            "${table}",
            "${name}",
            "${type}",
            "${null}",
            "${primary}",
            "${autoincrement}",
            "${unique}",
            "${index}",
        }
        for item in placeholders:
            stmt = stmt.replace(item, "")
        stmt = stmt.replace(" ;", ";")
        stmt = stmt.replace("  ", " ")
        return stmt.strip()

    def __init__(self, model):
        self.model = model

    @property
    def statement(self) -> str:
        if hasattr(self, "_statement"):
            return getattr(self, "_statement")

    @statement.setter
    def statement(self, value: str):
        setattr(self, "_statement", value)

    @statement.deleter
    def statement(self):
        if hasattr(self, "_statement"):
            delattr(self, "_statement")

    @property
    def typename(self):
        return self.__class__.__name__.lower()

    def execute(self):
        """Execute the sql statement."""
        if hasattr(self.model, "execute"):
            if hasattr(self, "params"):
                self.model.execute(sql=f"{self.statement};", params=self.params)
            else:
                self.model.execute(sql=f"{self.statement};")
        else:
            raise SqlExecutionError(
                "Failed to execute the SQL statement! "
                f"Object `{self.model.typename.title()}(name='{self.model.name}')` does not have an `execute` method!"
            )

    def query(self):
        """Execute the sql query."""
        if hasattr(self.model, "query"):
            if hasattr(self, "params"):
                return self.model.query(sql=f"{self.statement};", params=self.params)
            else:
                return self.model.query(sql=f"{self.statement};")
        else:
            raise SqlExecutionError(
                "Failed to execute the SQL query! "
                f"Object `{self.model.typename.title()}(name='{self.model.name}')` does not have a `query` method!"
            )

    def _resolve_parameters(self, *args, **kwargs):
        columns = [column.name for column in self.model.columns]

        if 0 < len(args) <= len(columns):
            kwargs, params = {columns[idx]: arg for idx, arg in enumerate(args)}, kwargs.copy()
            keys = set(kwargs).intersection(set(params))

            if len(keys) > 0:
                duplicates = ", ".join([f'"{key}"' for key in keys])
                raise ArgumentError(f"Columns({duplicates}) already passed through positional only args!")

            kwargs.update(params)

        if 0 <= len(kwargs) <= len(columns):
            for key, value in kwargs.items():

                if key not in columns:
                    raise ArgumentError(f"Column(name='{key}') not in Table(name='{self.model.name}')!")
            else:
                return kwargs
        else:
            raise ArgumentError(f"Failed to resolve the parameters for Table(name='{self.model.name}')!")

    def _resolve_tuples(self, *args):
        columns = [column.name for column in self.model.columns]
        if 0 < len(args) <= len(columns):
            for arg in args:
                key = arg.nt.column

                if key not in columns:
                    raise ArgumentError(f"Column(name='{key}') not in Table(name='{self.model.name}')!")
            else:
                return [f'"{arg.nt.column}" {arg.nt.operator} ?' for arg in args]
        else:
            raise ArgumentError(f"Failed to resolve the parameters for Table(name='{self.model.name}')!")


class Comparison(Statement):

    @staticmethod
    def _quote(value: Any):
        if (isinstance(value, str) is True) and (value not in ["NULL", "NOT NULL"]):
            value = f"'{value}'"
        return value

    def __call__(self, operator: str, value: Any):
        self.nt = COMPARISON(column=self.model.name, operator=operator, value=value)
        stmt = TEMPLATES.column.comparison.safe_substitute(
            column=f'"{self.nt.column}"',
            operator=self.nt.operator,
            value=self._quote(self.nt.value)
        )
        self.statement = self._clean(stmt)
        return self

    def __repr__(self):
        return self.statement


class BaseDDL(Statement):

    def __call__(self, *args, **kwargs):

        if self.model.typename == "table":
            self.statement = self._table(*args, **kwargs)

        elif self.model.typename == "index":
            self.statement = self._index(*args, **kwargs)

        return self

    @abstractmethod
    def _table(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _index(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.statement};"


class Create(BaseDDL):

    def __call__(self, if_not_exists: bool = False):
        return super(Create, self).__call__(if_not_exists=if_not_exists)

    def _table(self, if_not_exists: bool):
        values: dict = {
            "table": self.model.name,
        }

        if if_not_exists is True:
            values.update({"if_not_exists": "IF NOT EXISTS"})

        columns = list()
        for column in self.model.columns:
            columns.append(self._column_stmt(column))

        constraints = self._get_constraints()
        if constraints is not None:
            columns.append(constraints)

        values.update({"columns": ", ".join(columns)})

        stmt = TEMPLATES.table.create.safe_substitute(**values)
        return self._clean(stmt)

    def _column_stmt(self, column):

        fields = {
            "name": column.name,
            "type": column.type,
        }

        if column.null is False:
            fields.update({"null": "NOT NULL"})

        if column.unique is True:
            fields.update({"unique": "UNIQUE"})

        stmt = TEMPLATES.column.clause.safe_substitute(**fields)
        return self._clean(stmt)

    def _get_constraints(self):

        if self.model.autoincrement is not None:
            column = self.model.autoincrement[0]
            return f'PRIMARY KEY ("{column.name}" AUTOINCREMENT)'

        elif self.model.primary is not None:
            columns = [f'"{column.name}"' for column in self.model.primary]
            return f'PRIMARY KEY ({", ".join(columns)})'

    def _index(self, if_not_exists: bool) -> str:
        values = {
            "name": self.model.name,
            "table": self.model.table,
            "column": self.model.column,
        }

        if self.model.unique is True:
            values.update({"unique": "UNIQUE"})

        if if_not_exists is True:
            values.update({"if_not_exists": "IF NOT EXISTS"})

        stmt = TEMPLATES.index.create.safe_substitute(**values)
        return self._clean(stmt)


class Drop(BaseDDL):

    def __call__(self, if_exists: bool = False):
        return super(Drop, self).__call__(if_exists=if_exists)

    def _table(self, if_exists: bool) -> str:
        values = {
            "table": self.model.name,
        }

        if if_exists is True:
            values.update({"if_exists": "IF EXISTS"})

        stmt = TEMPLATES.table.drop.safe_substitute(**values)
        return self._clean(stmt)

    def _index(self, if_exists: bool) -> str:
        values = {
            "name": self.model.name,
        }

        if if_exists is True:
            values.update({"if_exists": "IF EXISTS"})

        stmt = TEMPLATES.index.drop.safe_substitute(**values)
        return self._clean(stmt)


class Insert(Statement):
    """INSERT INTO "${table}" (${columns}) VALUES (${values})"""

    def __init__(self, model):
        super(Insert, self).__init__(model)
        self.fields = {
            "table": self.model.name,
        }

    def __call__(self, *args, **kwargs):
        kwargs = self._resolve_parameters(*args, **kwargs)

        if len(kwargs) == 0:
            # noinspection PyProtectedMember
            kwargs = dict(self.model.columns._asdict())
        else:
            self.params = tuple(kwargs.values())

        self.fields.update({"columns": ", ".join([f'"{key}"' for key in kwargs.keys()])})
        self.fields.update({"values": ", ".join("?" * len(kwargs))})

        stmt = TEMPLATES.table.insert.safe_substitute(**self.fields)
        self.statement = self._clean(stmt)
        return self

    def __repr__(self):
        return f"{self.statement};"


class Update(Statement):

    def __init__(self, model):
        super(Update, self).__init__(model)
        self.template = TEMPLATES.table.update
        self.fields = {
            "table": self.model.name,
        }

    def __call__(self, *args, **kwargs):

        kwargs = self._resolve_parameters(*args, **kwargs)

        _fields = [f'"{key}" = ?' for key in kwargs.keys()]
        self.fields.update({"set": f"SET {', '.join(_fields)}"})

        stmt = self.template.safe_substitute(**self.fields)

        self.statement = self._clean(stmt)
        self.params = tuple(kwargs.values())

        return WhereClause(dml=self)


class Delete(Statement):

    def __init__(self, model):
        super(Delete, self).__init__(model)
        self.template = TEMPLATES.table.delete
        self.fields = {
            "table": self.model.name,
        }

    def __call__(self):
        stmt = self.template.safe_substitute(**self.fields)
        self.statement = self._clean(stmt)
        return WhereClause(dml=self)


class Select(Statement):

    def __init__(self, model):
        super(Select, self).__init__(model)

        self.template = TEMPLATES.table.select
        self.fields = {
            "table": self.model.name,
        }

    def __call__(self, *args):
        _fields = list()

        if len(args) == 0:
            _fields.append("*")

        else:
            for arg in args:
                # if isinstance(arg, str):
                #     _fields.append(arg)

                if hasattr(arg, "typename") is True:

                    if arg.typename == "column":
                        _fields.append(f'"{arg.name}"')

                    elif arg.typename in ["avg", "count", "max", "min", "sum"]:
                        _fields.append(f'"{arg.name}"')
                else:
                    raise ArgumentError("Bad parameter passed!")

        self.fields.update({"columns": ", ".join(_fields)})
        stmt = self.template.safe_substitute(**self.fields)
        self.statement = self._clean(stmt)
        return WhereClause(dml=self)


class AVG(Statement):

    def __call__(self):
        return f'AVG("{self.model.name}")'


class COUNT(Statement):

    def __call__(self):
        return f'COUNT("{self.model.name}")'


class MAX(Statement):

    def __call__(self):
        return f'MAX("{self.model.name}")'


class MIN(Statement):

    def __call__(self):
        return f'MIN("{self.model.name}")'


class SUM(Statement):

    def __call__(self):
        return f'SUM("{self.model.name}")'


class DISTINCT(Statement):

    def __call__(self):
        return f'DISTINCT("{self.model.name}")'


class WhereClause(Statement):

    def __init__(self, dml):
        super(WhereClause, self).__init__(model=dml.model)

        self.template = dml.template
        self.fields = dml.fields
        self.statement = dml.statement

        if hasattr(dml, "params"):
            self.params = dml.params

    def where(self, *args):
        _fields = self._resolve_tuples(*args)

        self.fields.update({"where": f"WHERE {' AND '.join(_fields)}"})
        stmt = self.template.safe_substitute(**self.fields)

        self.statement = self._clean(stmt)

        if hasattr(self, "params"):
            self.params = self.params + tuple(arg.nt.value for arg in args)
        else:
            self.params = tuple(arg.nt.value for arg in args)

        return LogicalOperator(dml=self)


class LogicalOperator(Statement):

    def __init__(self, dml):
        super(LogicalOperator, self).__init__(model=dml.model)

        self.statement = dml.statement
        self.params = dml.params

    def and_(self, *args):
        _fields = self._resolve_tuples(*args)

        self.statement = f"{self.statement} AND {' AND '.join(_fields)}"
        self.params = self.params + tuple(arg.nt.value for arg in args)

        return self

    def or_(self, *args):
        _fields = self._resolve_tuples(*args)

        self.statement = f"{self.statement} OR {' AND '.join(_fields)}"
        self.params = self.params + tuple(arg.nt.value for arg in args)

        return self


class DDL(Statement):

    def __init__(self, model):
        super(DDL, self).__init__(model)

        self._create = Create(model)
        self._drop = Drop(model)

    def create(self, if_not_exists: bool = False):
        return self._create(if_not_exists)

    def drop(self, if_exists: bool = False):
        return self._drop(if_exists)


class DML(Statement):

    def __init__(self, model):
        super(DML, self).__init__(model)

        self._insert = Insert(model)
        self._update = Update(model)
        self._delete = Delete(model)

    def insert(self, *args, **kwargs):
        return self._insert(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._update(*args, **kwargs)

    def delete(self):
        return self._delete()


class DQL(Statement):

    def __init__(self, model):
        super(DQL, self).__init__(model)
        self._select = Select(model)

    def select(self, *args):
        return self._select(*args)