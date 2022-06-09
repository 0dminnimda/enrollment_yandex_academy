from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeInt

from .docs import schemas
from .typedefs import BaseModelT, T


def wrap_schema(cls: BaseModelT) -> BaseModelT:
    schema = schemas[cls.__name__]
    properties = schema["properties"]

    atribures = dict(
        schema_extra={"example": schema.get("example", {})}
    )

    if not hasattr(cls, "Config"):
        cls.Config = type("Config")  # type: ignore

    Config = cls.Config

    for name, value in atribures.items():
        setattr(Config, name, value)

    for name, field in cls.__fields__.items():
        field.field_info.description = properties[name].get("description")

    return cls


def with_name(name: str):
    def decorator(o: T) -> T:
        o.__name__ = name
        # o.__qualname__ = name
        return o
    return decorator


class ShopUnitType(str, Enum):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"


ShopUnitType.__doc__ = schemas["ShopUnitType"]["description"]


class BaseInfo(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID] = None
    type: ShopUnitType
    price: Optional[NonNegativeInt] = None


@wrap_schema
class ShopUnit(BaseInfo):
    date: datetime
    children: Optional[List[ShopUnit]] = None


ShopUnit.update_forward_refs()


@wrap_schema
@with_name("ShopUnitImport")
class Import(BaseInfo):
    pass


@wrap_schema
@with_name("ShopUnitImportRequest")
class ImpRequest(BaseModel):
    items: List[Import]
    updateDate: datetime


@wrap_schema
@with_name("ShopUnitStatisticUnit")
class StatUnit(BaseInfo):
    date: datetime


@wrap_schema
@with_name("ShopUnitStatisticResponse")
class StatResponse(BaseModel):
    items: List[StatUnit]


class Error(BaseModel):
    code: int
    message: str
