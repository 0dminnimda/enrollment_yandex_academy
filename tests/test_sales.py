from datetime import datetime

from fastapi.testclient import TestClient
from SBDY_app.schemas import ShopUnit, StatResponse, StatUnit

from utils import ERROR_400, client, default, do_test, setup


setup()


def test_ok(client: TestClient):
    date = default(datetime)
    response = client.get("/sales", params={"date": date})
    assert response.status_code == 200
    assert response.json() == StatResponse(items=[])

    unit = default(ShopUnit)
    # TODO: create a unit in a db

    date = default(datetime)
    response = client.get("/sales", params={"date": date})
    assert response.status_code == 200
    assert response.json() == StatResponse(items=[StatUnit(**unit.dict())])


def test_validation(client: TestClient):
    response = client.get("/sales")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.get("/sales", params={"date": "abooba"})
    assert response.status_code == 400
    assert response.json() == ERROR_400

    # logically should not be allowed, but by the rules this is not checked,
    # so no additional pain trying to disallow this ;)
    # response = client.get("/sales", params={"date": "42069"})
    # assert response.status_code == 400
    # assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
