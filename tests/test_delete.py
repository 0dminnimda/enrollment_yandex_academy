from uuid import UUID

from utils import ERROR_400, ERROR_404, Client, client, default, do_test, setup

setup()


def test_delete(client: Client):
    id = default(UUID)
    # TODO: adding the unit with id to the db

    response = client.delete(id)
    assert response.status_code == 200

    # TODO: check that the unit is deleted

    response = client.delete(id)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    # TODO: check that the unit is still deleted


def test_nonexisting_items(client: Client):
    response = client.delete(default(UUID))
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.delete(default(UUID))
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: Client):
    response = client.delete("abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.delete("42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.delete("3fa85f64-5717-4562-b3fc")
    assert response.status_code == 400
    assert response.json() == ERROR_400


# TODO: removing category removes its children


if __name__ == "__main__":
    do_test(__file__)
