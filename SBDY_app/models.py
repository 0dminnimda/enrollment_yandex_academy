"""
Database models
    Fields of the models are annotated by their python type
    so typecheckers can really help with code that uses models
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeMeta, declarative_base, relationship
from sqlalchemy_utils import UUIDType

from .schemas import ShopUnitType


Base: DeclarativeMeta = declarative_base()


class Depth(Base):
    __tablename__ = 'depth'

    id: int = Column(Integer, primary_key=True, unique=True)  # type: ignore
    depth: int = Column(Integer)  # type: ignore


class ShopUnit(Base):
    __tablename__ = 'shop'

    id: UUID = Column(  # type: ignore
        UUIDType(), primary_key=True, unique=True)
    parentId: UUID = Column(  # type: ignore
        UUIDType(), ForeignKey('shop.id'), nullable=True)
    children: List[ShopUnit] = relationship("ShopUnit")  # type: ignore

    name: str = Column(String)  # type: ignore
    type: ShopUnitType = Column(Enum(ShopUnitType))  # type: ignore
    price: int = Column(Integer, nullable=True)  # type: ignore
    date: datetime = Column(DateTime)  # type: ignore
