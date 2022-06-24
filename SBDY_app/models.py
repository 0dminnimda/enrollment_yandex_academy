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


class ShopUnit(Base):
    __tablename__ = "shop"

    id: UUID = Column(UUIDType(), primary_key=True)  # type: ignore
    parentId: Optional[UUID] = Column(  # type: ignore
        UUIDType(), ForeignKey("shop.id"), nullable=True)
    children: List[ShopUnit]

    name: str = Column(String)  # type: ignore
    date: datetime = Column(DateTime)  # type: ignore

    type: ShopUnitType = Column(Enum(ShopUnitType))  # type: ignore
    price: int = Column(Integer)  # type: ignore
    sub_offers_count: int = Column(Integer)  # type: ignore
