from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from .docs import openapi


schemas = openapi["components"]["schemas"]


BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])


def wrap_schema(cls: BaseModelT) -> BaseModelT:
    schema = schemas[cls.__name__]
    properties = schema["properties"]

    class Config:
        schema_extra = {"example": schema.get("example", {})}

    cls.Config = Config  # type: ignore

    for name, field in cls.__fields__.items():
        field.field_info.description = properties[name].get("description")

    return cls


class ShopUnitType(str, Enum):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"


ShopUnitType.__doc__ = schemas["ShopUnitType"]["description"]


class BaseInfo(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID] = None
    type: ShopUnitType
    price: int = 0


@wrap_schema
class ShopUnit(BaseInfo):
    date: datetime
    children: Optional[List[ShopUnit]] = None


ShopUnit.update_forward_refs()


@wrap_schema
class ShopUnitImport(BaseInfo):
    pass


Import = ShopUnitImport


@wrap_schema
class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport]
    updateDate: datetime


ImpRequest = ShopUnitImportRequest


@wrap_schema
class ShopUnitStatisticUnit(BaseInfo):
    date: datetime


StatUnit = ShopUnitStatisticUnit


@wrap_schema
class ShopUnitStatisticResponse(BaseModel):
    items: List[ShopUnitStatisticUnit]


StatResponse = ShopUnitStatisticResponse


class Error(BaseModel):
    code: int
    message: str
