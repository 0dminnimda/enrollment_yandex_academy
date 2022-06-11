from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession as DB


AnyCallable = Callable[..., Any]
BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])
T = TypeVar("T", bound=Any)
