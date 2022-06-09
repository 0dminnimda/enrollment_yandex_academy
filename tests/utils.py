"""
Things that simplify the testing process and help with it
"""

import random
import string
from datetime import datetime
from pathlib import Path
from typing import List, Type, TypeVar, _GenericAlias  # type: ignore
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from SBDY_app import app
from SBDY_app.schemas import Error, ShopUnitType


def setup():
    random.seed(69)


### pytest ###

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def do_test(file: str) -> None:
    pytest.main([file, "-W", "ignore::pytest.PytestAssertRewriteWarning"])


### Link to the server deployed in the container ###

container_link_raw = "https://{nickname}.usr.yandex-academy.ru/"
_secrets = Path(__file__).parent / "my_secrets.py"
_template = Path(__file__).parent / "my_secrets.py_template"


def container_link() -> str:
    _secrets_rel = _secrets.relative_to(Path.cwd())
    _template_rel = _template.relative_to(Path.cwd())

    if not _secrets.exists():
        _secrets.touch()
        print(
            "\n"
            f"⚠ File '{_secrets_rel}' didn't exist, but I created it for you\n"
            f"⚠ Fill it out like in '{_template_rel}':\n"
            "\n"
            f"{_template.read_text()}"
        )
        raise FileNotFoundError(f"File '{_secrets}' didn't exist")

    args: dict = {}
    exec(_secrets.read_text(), args)

    if "nickname" not in args:
        print(
            "\n"
            f"⚠ File '{_secrets_rel}' isn't filled out correctly\n"
            f"⚠ Fill it out like in '{_template_rel}':\n"
            "\n"
            f"{_template.read_text()}"
        )
        raise NameError(
            f"Name 'nickname' is not found in '{_secrets_rel}',"
            " it's required by 'container_link'")

    return container_link_raw.format(**args)


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
