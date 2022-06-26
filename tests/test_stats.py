import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, StatResponse, StatUnit

from utils import ERROR_400, ERROR_404, Client, client, default, do_test, setup

setup()


def test_ok(client: Client):
    imp = default(Import, parentId=None)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    model = {"items": [{**json.loads(imp.json()),
                        "date": serialize_datetime(data.updateDate)}]}

    response = client.stats(imp.id)
    assert response.status_code == 200
    assert response.json() == model


def shifted_stat(client: Client, id: Any, start: datetime,
                 end: datetime, shift: timedelta):
    return client.stats(id, start + shift, end + shift)


def test_boundaries(client: Client):
    date = default(datetime)
    imp = default(Import, parentId=None)
    response = client.imports(default(
        ImpRequest, items=[imp], updateDate=date).json())
    assert response.status_code == 200

    start, end = date - timedelta(days=1), date
    model = {"items": [{**json.loads(imp.json()),
                        "date": serialize_datetime(date)}]}

    response = client.stats(imp.id, start)
    assert response.status_code == 200
    assert response.json() == model

    response = client.stats(imp.id, start, end)
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = shifted_stat(client, imp.id, start, end,
                            timedelta(milliseconds=1))
    assert response.status_code == 200
    assert response.json() == model

    response = shifted_stat(client, imp.id, start, end, timedelta(days=1))
    assert response.status_code == 200
    assert response.json() == model

    response = shifted_stat(client, imp.id, start, end,
                            timedelta(days=1, milliseconds=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = shifted_stat(client, imp.id, start, end, -timedelta(days=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = shifted_stat(client, imp.id, start, end,
                            -timedelta(milliseconds=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_deletion(client: Client):
    imp = default(Import, parentId=None)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    model = {"items": [{**json.loads(imp.json()),
                        "date": serialize_datetime(data.updateDate)}]}

    response = client.stats(imp.id)
    assert response.status_code == 200
    assert response.json() == model

    response = client.delete(imp.id)
    assert response.status_code == 200

    response = client.stats(imp.id)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    imp = default(Import, id=imp.id, parentId=None)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    model = {"items": [{**json.loads(imp.json()),
                        "date": serialize_datetime(data.updateDate)}]}

    response = client.stats(imp.id)
    assert response.status_code == 200
    assert response.json() == model


def test_nonexistent(client: Client):
    response = client.stats(default(UUID))
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.stats(default(UUID), dateStart=default(datetime))
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.stats(default(UUID), dateEnd=default(datetime))
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.stats(
        default(UUID), dateStart=default(datetime), dateEnd=default(datetime))
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: Client):
    response = client.stats("abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.stats("42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    imp = default(Import, parentId=None)
    response = client.imports(default(ImpRequest, items=[imp]).json())
    assert response.status_code == 200

    response = client.stats(imp.id, dateStart="abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.stats(imp.id, dateStart="42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.stats(imp.id, dateEnd="abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.stats(imp.id, dateEnd="42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
