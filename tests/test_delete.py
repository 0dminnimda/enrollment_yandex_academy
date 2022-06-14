from uuid import UUID
from SBDY_app.schemas import ImpRequest, Import, ShopUnitType

from utils import ERROR_400, ERROR_404, Client, client, default, do_test, setup

setup()


def test_delete(client: Client):
    id = default(UUID)
    data = default(ImpRequest, items=[default(Import, id=id, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.delete(id)
    assert response.status_code == 200

    response = client.nodes(id)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.delete(id)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.nodes(id)
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_delete_hierarchy(client: Client):
    id1, id2 = default(UUID), default(UUID)
    items = [
        default(Import, id=id1, parentId=None,
                type=ShopUnitType.CATEGORY, price=None),
        default(Import, id=id2, parentId=id1)]
    data = default(ImpRequest, items=items)
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.delete(id1)
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 404
    assert response.json() == ERROR_404
    response = client.nodes(id2)
    assert response.status_code == 404
    assert response.json() == ERROR_404


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
