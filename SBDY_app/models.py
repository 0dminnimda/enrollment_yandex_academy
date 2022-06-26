"""
Database models
    Fields of the models are annotated by their python type
    so typecheckers can really help with code that uses models
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeMeta, declarative_base, relationship
from sqlalchemy_utils import UUIDType

from .schemas import ShopUnitType


# for future: github.com/tiangolo/sqlmodel
# may be a better way to handle typechecking + reuse code
Base: DeclarativeMeta = declarative_base()


class BaseUnit:
    name: str = Column(String)  # type: ignore
    date: datetime = Column(DateTime)  # type: ignore

    type: ShopUnitType = Column(Enum(ShopUnitType))  # type: ignore
    price: int = Column(Integer)  # type: ignore
    sub_offers_count: int = Column(Integer)  # type: ignore

    @classmethod
    def _fields(cls) -> List[str]:
        result = cls.__annotations__.keys()
        if issubclass(cls, Base):
            result |= cls._sa_class_manager.keys()  # type: ignore
        return sorted(result)

    def __repr__(self) -> str:
        kv = {}
        for name in self._fields():
            try:
                kv[name] = getattr(self, name)
            except Exception as e:
                kv[name] = f"[Error while getting - {e}]"
        pairs = (f"{name}={repr(value)}" for name, value in kv.items())
        return f"{type(self).__name__}({', '.join(pairs)})"


class ShopUnit(Base, BaseUnit):
    __tablename__ = "shop"

    id: UUID = Column(UUIDType(), primary_key=True)  # type: ignore
    parentId: Optional[UUID] = Column(  # type: ignore
        UUIDType(), ForeignKey("shop.id"), nullable=True)
    children: List[ShopUnit]


class StatUnit(Base, BaseUnit):
    __tablename__ = "stat"

    _unique_id = Column(Integer, primary_key=True, autoincrement=True)
    id: UUID = Column(UUIDType())  # type: ignore
    parentId: Optional[UUID] = Column(  # type: ignore
        UUIDType(), nullable=True)
