from datetime import datetime
from enum import Enum
from typing import List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from .docs import openapi


schemas = openapi["components"]["schemas"]


BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])


def wrap_schema(cls: BaseModelT, name: Optional[str] = None) -> BaseModelT:
    if name is None:
        name = cls.__name__
    schema = schemas[name]
    properties = schema["properties"]

    class Config:
        schema_extra = {"example": schema.get("example", {})}

    cls.Config = Config  # type: ignore

    for name, field in cls.__fields__.items():
        field.field_info.description = properties[name].get("description")

    return cls


def wrap_other_schema(name: str):
    def wrapper(cls: BaseModelT) -> BaseModelT:
        return wrap_schema(cls, name)
    return wrapper


class ShopUnitType(str, Enum):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"


ShopUnitType.__doc__ = schemas["ShopUnitType"]["description"]


@wrap_schema
class ShopUnitImport(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID] = None
    type: ShopUnitType
    price: int = 0


@wrap_schema
class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport]
    updateDate: datetime


class Error(BaseModel):
    code: int
    message: str
