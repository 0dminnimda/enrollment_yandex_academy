from uuid import UUID
from fastapi.testclient import TestClient

from utils import ERROR_400, ERROR_404, client, default, do_test, setup


setup()


def test_delete(client: TestClient):
    id = default(UUID)
    # TODO: adding the entry with id to the db

    response = client.delete(f"/delete/{id}")
    assert response.status_code == 200

    # TODO: check that the entry is deleted

    response = client.delete(f"/delete/{id}")
    assert response.status_code == 404
    assert response.json() == ERROR_404

    # TODO: check that the entry is still deleted


def test_nonexisting_items(client: TestClient):
    response = client.delete(f"/delete/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.delete(f"/delete/{default(UUID)}")
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: TestClient):
    response = client.delete(f"/delete/{default(str)}")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.delete(f"/delete/{default(int)}")
    assert response.status_code == 400
    assert response.json() == ERROR_400


# TODO: removing category removes its children


if __name__ == "__main__":
    do_test(__file__)
