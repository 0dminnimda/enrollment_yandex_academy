from uuid import UUID

from SBDY_app.schemas import ShopUnit

from utils import ERROR_400, ERROR_404, Client, client, default, do_test, setup

setup()


def test_unit(client: Client):
    id = default(UUID)
    # TODO: adding the unit with id to the db

    response = client.get(id)
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_empty_category(client: Client):
    id = default(UUID)
    # TODO: adding the category without children with id to the db

    response = client.get(id)
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_full_category(client: Client):
    id = default(UUID)
    # TODO: adding the category with children with id to the db

    response = client.get(id)
    assert response.status_code == 200
    # TODO: check that the item is the same
    thing = ShopUnit(**response.json())  # no ValidationError

    # TODO: check that the unit is still there
    # unchanged and matches the response


def test_nonexisting_items(client: Client):
    response = client.get(f"/nodes/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.get(f"/nodes/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: Client):
    response = client.get("abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.get("42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
