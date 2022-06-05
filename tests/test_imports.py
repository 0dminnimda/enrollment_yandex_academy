from fastapi.testclient import TestClient
from SBDY_app.models import Import, ImpRequest

from utils import ERROR_400, client, default, do_test, setup


setup()


def test_ok(client: TestClient):
    data = default(ImpRequest, items=[])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    data = default(ImpRequest)
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    data = default(ImpRequest, items=[default(Import), default(Import)])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200


def test_validation(client: TestClient):
    data = default(ImpRequest, items=[]).json(exclude={"items"})
    response = client.post("/imports", data=data)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    data = default(ImpRequest).json(exclude={"updateDate"})
    response = client.post("/imports", data=data)
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
