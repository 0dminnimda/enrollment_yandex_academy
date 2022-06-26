"""
Things that simplify the testing process and help with it
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import _GenericAlias  # type: ignore
from typing import Any, Generator, Optional, Type
from urllib.parse import urljoin
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from requests import Session
from SBDY_app import app, options
from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Error, ShopUnitType
from SBDY_app.typedefs import T


def setup():
    random.seed(69)
    options.DEV_MODE = True


### Link to the server deployed in the container ###

container_link_raw = "https://{nickname}.usr.yandex-academy.ru"
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


### pytest ###

LOCAL = True
PROFILE = False


class Client:
    client: Session

    def __init__(self, client: Session, base_url: str):
        def request(method, url, *args, **kwargs):  # type: ignore
            url = urljoin(base_url, url)
            return Session.request(client, method, url, *args, **kwargs)

        client.request = request  # type: ignore
        client.base_url = base_url  # type: ignore
        self.client = client

    def cleanup_database(self):
        return self.client.delete("/_cleanup_database_")

    def imports(self, data: str):
        return self.client.post("/imports", data=data)

    def delete(self, id: Any):
        return self.client.delete(f"/delete/{id}")

    def nodes(self, id: Any):
        return self.client.get(f"/nodes/{id}")

    def sales(self, date: Any = None):
        if isinstance(date, datetime):
            date = serialize_datetime(date)

        params = {}
        if date is not None:
            params["date"] = date
        return self.client.get("/sales", params=params)

    def stats(self, id: Any, dateStart: Any = None, dateEnd: Any = None):
        if isinstance(dateStart, datetime):
            dateStart = serialize_datetime(dateStart)
        if isinstance(dateEnd, datetime):
            dateEnd = serialize_datetime(dateEnd)

        params = {}
        if dateStart is not None:
            params["dateStart"] = dateStart
        if dateEnd is not None:
            params["dateEnd"] = dateEnd
        return self.client.get(f"/node/{id}/statistic", params=params)

    def __enter__(self) -> Client:
        self.client.__enter__()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.client.__exit__(*args, **kwargs)


def generate_client() -> Client:
    if LOCAL:
        if PROFILE:
            base_url = "http://localhost:80"
            cl = Session()
        else:
            base_url = "http://testserver"
            cl = TestClient(app)
    else:
        base_url = container_link()
        cl = Session()

    return Client(cl, base_url)


@pytest.fixture
def client() -> Generator[Client, None, None]:
    options.DEV_MODE = True
    with generate_client() as client:
        client.cleanup_database()
        yield client


def do_test(file: str) -> None:
    pytest.main([
        file, "-vv", "-W", "ignore::pytest.PytestAssertRewriteWarning"])


### json ###

ERROR_400 = Error(code=400, message="Validation Failed")
ERROR_404 = Error(code=404, message="Item not found")


### default ###

def random_string() -> str:
    # in case you want use:
    # NORMAL_CHARS = string.digits + string.ascii_letters + string.whitespace
    return "".join(
        random.choice(string.printable)
        for _ in range(random.randint(5, 25)))


def random_su_type() -> ShopUnitType:
    return ShopUnitType.OFFER
    # if random.randint(0, 1):
    # return ShopUnitType.CATEGORY


def random_date(start: datetime = datetime.min,
                end: datetime = datetime.max) -> datetime:
    delta = end - start
    microseconds = ((delta.days * (24 * 3600) + delta.seconds) * 1000000
                    + delta.microseconds)
    return start + timedelta(microseconds=random.randrange(microseconds))


factories = {
    str: random_string,
    UUID: uuid4,
    ShopUnitType: random_su_type,
    int: lambda: random.randint(0, 10**5),
    datetime: random_date  # datetime.today
}


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

        for tp, func in factories.items():
            if issubclass(cls, tp):
                return func()

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
