"""
Things that simplify the testing process and help with it
"""

import random
import string
from datetime import datetime
from typing import List, Type, TypeVar, _GenericAlias  # type: ignore
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from SBDY_app import app
from SBDY_app.models import ShopUnitType, Error


def setup():
    random.seed(69)


### pytest ###

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def do_test(file: str) -> None:
    pytest.main([file, "-W", "ignore::pytest.PytestAssertRewriteWarning"])


### json ###

ERROR_400 = Error(code=400, message="Validation Failed")
ERROR_404 = Error(code=404, message="Item not found")


### default ###

def random_string() -> str:
    return "".join(
        random.choice(string.printable)
        for _ in range(random.randint(5, 25)))


def random_su_type() -> ShopUnitType:
    if random.randint(0, 1):
        return ShopUnitType.OFFER
    return ShopUnitType.CATEGORY


factories = {
    str: random_string,
    UUID: uuid4,
    ShopUnitType: random_su_type,
    int: lambda: random.randint(0, 10**5),
    datetime: datetime.today
}


T = TypeVar("T")


class ImpossibleRecursiveDefinition(Exception):
    message: str = (
        "Cannot make a default class instance, definition is recursive,"
        " there is no possibility to ignore the recursion.")

    def __init__(self):
        super().__init__(self.message)


def default(cls: Type[T], **defaults) -> T:
    def _default(cls, visited, defaults):
        if cls in factories:
            return factories[cls]()

        if isinstance(cls, _GenericAlias) and cls._name == "List":
            try:
                return [_default(cls.__args__[0], visited, {})]
            except ImpossibleRecursiveDefinition:
                return []

        try:
            fields: dict = cls.__fields__
        except AttributeError:
            raise TypeError("'default' only works with pydantic models,"
                            f" basic types and typing.List-s, found {cls}!")

        if cls in visited:
            raise ImpossibleRecursiveDefinition
        visited.add(cls)
        for name in fields.keys() - defaults.keys():
            defaults[name] = _default(fields[name].outer_type_, visited, {})

        return cls(**defaults)

    visited = set()  # type: ignore
    return _default(cls, visited, defaults)
