from enum import Enum
from typing import List, Optional, Type
from uuid import UUID

from pydantic import BaseModel, Field

from .docs import openapi

schemas = openapi["components"]["schemas"]


def wrap_schema(cls: Type[BaseModel]) -> Type[BaseModel]:
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
    updateDate: str


class Error(BaseModel):
    code: int
    message: str
