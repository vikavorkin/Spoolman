"""Utility functions for the database module."""

from collections.abc import Sequence
from enum import Enum
from typing import Any, Optional, Union

import sqlalchemy
from sqlalchemy import Select
from sqlalchemy.orm import attributes

from spoolman.database import models


class SortOrder(Enum):
    ASC = 1
    DESC = 2


def parse_nested_field(base_obj: type[models.Base], field: str) -> attributes.InstrumentedAttribute[Any]:
    """Parse a nested field string into a sqlalchemy field object."""
    fields = field.split(".")
    if not hasattr(base_obj, fields[0]):
        raise ValueError(f"Invalid field name '{field}', '{fields[0]}' is not a valid field on '{base_obj.__name__}'.")

    if fields[0] == "filament" and len(fields) == 1:
        raise ValueError("No field specified for filament")
    if fields[0] == "filament":
        return parse_nested_field(models.Filament, ".".join(fields[1:]))

    if fields[0] == "vendor" and len(fields) == 1:
        raise ValueError("No field specified for vendor")
    if fields[0] == "vendor":
        return parse_nested_field(models.Vendor, ".".join(fields[1:]))

    if len(fields) > 1:
        raise ValueError(f"Field '{fields[0]}' does not have any nested fields")

    return getattr(base_obj, fields[0])


def add_where_clause_str_opt(
    stmt: Select,
    field: attributes.InstrumentedAttribute[Optional[str]],
    value: Optional[str],
) -> Select:
    """Add a where clause to a select statement for an optional string field."""
    if value is not None:
        if len(value) == 0:
            stmt = stmt.where(sqlalchemy.or_(field.is_(None), field == ""))
        else:
            stmt = stmt.where(sqlalchemy.or_(*(field.ilike(f"%{value}%") for value in value.split(","))))
    return stmt


def add_where_clause_str(
    stmt: Select,
    field: attributes.InstrumentedAttribute[str],
    value: Optional[str],
) -> Select:
    """Add a where clause to a select statement for a string field."""
    if value is not None:
        if len(value) == 0:
            stmt = stmt.where(field == "")
        else:
            stmt = stmt.where(sqlalchemy.or_(*(field.ilike(f"%{value}%") for value in value.split(","))))
    return stmt


def add_where_clause_int(
    stmt: Select,
    field: attributes.InstrumentedAttribute[int],
    value: Optional[Union[int, Sequence[int]]],
) -> Select:
    """Add a where clause to a select statement for a field."""
    if value is not None:
        if isinstance(value, int):
            value = [value]
        stmt = stmt.where(field.in_(value))
    return stmt


def add_where_clause_int_opt(
    stmt: Select,
    field: attributes.InstrumentedAttribute[Optional[int]],
    value: Optional[Union[int, Sequence[int]]],
) -> Select:
    """Add a where clause to a select statement for a field."""
    if value is not None:
        if isinstance(value, int):
            value = [value]
        statements = []
        for value_part in value:
            if value_part == -1:
                statements.append(field.is_(None))
            else:
                statements.append(field == value_part)
        stmt = stmt.where(sqlalchemy.or_(*statements))
    return stmt
