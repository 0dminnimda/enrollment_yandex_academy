import json
from datetime import datetime, timedelta

from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, StatResponse

from utils import ERROR_400, Client, client, default, do_test, setup

setup()


def test_ok(client: Client):
    date = default(datetime)
    response = client.sales(date)
    assert response.status_code == 200
    assert response.json() == StatResponse(items=[])


def test_boundaries(client: Client):
    date = default(datetime)
    imp = default(Import, parentId=None)
    response = client.imports(default(
        ImpRequest, items=[imp], updateDate=date).json())
    assert response.status_code == 200

    data = {"items": [{**json.loads(imp.json()),
                       "date": serialize_datetime(date)}]}
    response = client.sales(date)
    assert response.status_code == 200
    assert response.json() == data

    response = client.sales(date + timedelta(milliseconds=1))
    assert response.status_code == 200
    assert response.json() == data

    response = client.sales(date + timedelta(days=1))
    assert response.status_code == 200
    assert response.json() == data

    response = client.sales(date + timedelta(days=1, milliseconds=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = client.sales(date - timedelta(days=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}

    response = client.sales(date - timedelta(milliseconds=1))
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_validation(client: Client):
    response = client.sales()
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.sales("abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.sales("42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
