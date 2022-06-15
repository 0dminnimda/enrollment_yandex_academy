from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (BaseModel, Field, NonNegativeInt, root_validator,
                      validator)

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

    @root_validator
    def ensure_children_and_price(cls, values):
        tp = values.get("type", None)
        if tp == ShopUnitType.OFFER:
            values["children"] = None
        elif tp == ShopUnitType.CATEGORY:
            children = values.get("children", [])
            # sanity check because in db it's stored as a list
            assert isinstance(children, list)

            if len(children) == 0:
                values["price"] = None

        return values

    class Config:
        orm_mode = True


ShopUnit.update_forward_refs()


@wrap_schema
@with_name("ShopUnitImport")
class Import(BaseInfo):
    @root_validator
    def price_is_fine(cls, values):
        tp = values.get("type", None)
        if tp == ShopUnitType.CATEGORY:
            if values.get("price", None) is not None:
                # only for import
                raise ValueError("'price' of the categories should be null")
            else:
                # but make it int for db
                values["price"] = 0
        elif tp == ShopUnitType.OFFER:
            if values.get("price", None) is None:
                raise ValueError("'price' of the offer should not be null")
        return values


@wrap_schema
@with_name("ShopUnitImportRequest")
class ImpRequest(BaseModel):
    items: List[Import]
    updateDate: datetime

    @validator('items')
    def ids_are_unique(cls, items: List[Import]) -> List[Import]:
        seen = set()
        if any(i.id in seen or seen.add(i.id) for i in items):  # type: ignore
            raise ValueError("All 'id's of the 'items' should be unique")
        return items


@wrap_schema
@with_name("ShopUnitStatisticUnit")
class StatUnit(BaseInfo):
    date: datetime

    class Config:
        orm_mode = True


@wrap_schema
@with_name("ShopUnitStatisticResponse")
class StatResponse(BaseModel):
    items: List[StatUnit]


class Error(BaseModel):
    code: int
    message: str
