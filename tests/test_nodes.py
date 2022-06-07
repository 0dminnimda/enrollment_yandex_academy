from uuid import UUID

from fastapi.testclient import TestClient
from SBDY_app.models import ShopUnit

from utils import ERROR_400, ERROR_404, client, default, do_test, setup


setup()


def test_unit(client: TestClient):
    id = default(UUID)
    # TODO: adding the unit with id to the db

    response = client.get(f"/nodes/{id}")
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_empty_category(client: TestClient):
    id = default(UUID)
    # TODO: adding the category without children with id to the db

    response = client.get(f"/nodes/{id}")
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_full_category(client: TestClient):
    id = default(UUID)
    # TODO: adding the category with children with id to the db

    response = client.get(f"/nodes/{id}")
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_nonexisting_items(client: TestClient):
    response = client.get(f"/nodes/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.get(f"/nodes/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: TestClient):
    response = client.get(f"/nodes/abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.get(f"/nodes/42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
