from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeMeta, declarative_base, relationship
from sqlalchemy_utils import UUIDType

from .schemas import ShopUnitType


Base: DeclarativeMeta = declarative_base()


class Depth(Base):
    __tablename__ = 'depth'

    id = Column(Integer, primary_key=True, unique=True)

    depth = Column(Integer)


class ShopUnit(Base):
    __tablename__ = 'shop'

    id = Column(UUIDType(), primary_key=True, unique=True)
    parentId = Column(UUIDType(), ForeignKey('shop.id'), nullable=True)
    children = relationship("ShopUnit")

    name = Column(String)
    type = Column(Enum(ShopUnitType))
    price = Column(Integer, nullable=True)
    date = Column(DateTime)
