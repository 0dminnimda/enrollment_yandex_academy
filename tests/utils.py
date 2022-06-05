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
from SBDY_app.models import ShopUnitType


def setup():
    random.seed(69)


### pytest ###

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def do_test(file: str) -> None:
    pytest.main([file, "-W", "ignore::pytest.PytestAssertRewriteWarning"])


### json ###

ERROR_400 = {"code": 400, "message": "Validation Failed"}


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


def default(cls: Type[T], **defaults) -> T:
    if cls in factories:
        return factories[cls]()  # type: ignore

    if isinstance(cls, _GenericAlias) and cls._name == "List":  # type: ignore
        return [default(cls.__args__[0])]  # type: ignore

    try:
        fields: dict = cls.__fields__  # type: ignore
    except AttributeError:
        raise TypeError("'default' only works with pydantic models,"
                        f" basic types and typing.List-s, found {cls}!")

    for name in fields.keys() - defaults.keys():
        defaults[name] = default(fields[name].outer_type_)

    return cls(**defaults)  # type: ignore

# def default(cls, **kwargs):
#     default = dict(
#         id=uuid4(), name=random_string(),
#         parentId=uuid4(), type=random_su_type(),
#         price=random.randint(0, 10**5), date=datetime.today(),
#         updateDate=datetime.today())

#     default.update(kwargs)
#     return cls(**default)
