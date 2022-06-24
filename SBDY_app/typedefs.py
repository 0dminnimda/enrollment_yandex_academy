from typing import TYPE_CHECKING, Any, Callable, Dict, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession as DB

if TYPE_CHECKING:
    from .models import ShopUnit


AnyCallable = Callable[..., Any]
BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])
T = TypeVar("T", bound=Any)
ShopUnits = Dict[UUID, "ShopUnit"]
