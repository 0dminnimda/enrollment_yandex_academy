from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel


AnyCallable = Callable[..., Any]
BaseModelT = TypeVar("BaseModelT", bound=Type[BaseModel])
T = TypeVar("T", bound=Any)
