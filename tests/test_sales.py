from datetime import datetime

from SBDY_app.schemas import ShopUnit, StatResponse, StatUnit

from utils import ERROR_400, Client, client, default, do_test, setup

setup()


def test_ok(client: Client):
    date = default(datetime)
    response = client.sales(date)
    assert response.status_code == 200
    assert response.json() == StatResponse(items=[])

    unit = default(ShopUnit)
    # TODO: create a unit in a db

    date = default(datetime)
    response = client.sales(date)
    assert response.status_code == 200
    assert response.json() == StatResponse(items=[StatUnit(**unit.dict())])


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
