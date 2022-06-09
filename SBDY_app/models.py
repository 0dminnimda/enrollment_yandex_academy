from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeInt


BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])
from .docs import schemas


def wrap_schema(cls: BaseModelT) -> BaseModelT:
    schema = schemas[cls.__name__]
    properties = schema["properties"]

    class Config:
        schema_extra = {"example": schema.get("example", {})}

    cls.Config = Config  # type: ignore

    for name, field in cls.__fields__.items():
        field.field_info.description = properties[name].get("description")

    return cls


T = TypeVar("T", bound=Any)


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
