import json
from uuid import UUID

from SBDY_app import options
from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, ShopUnit, ShopUnitType

from utils import (ERROR_400, ERROR_404, PROFILE, Client, client, default,
                   do_test, generate_client, setup)

setup()


def test_ok(client: Client):
    response = client.cleanup_database()
    assert response.status_code == 200


def test_mode():
    if PROFILE:
        return

    original_mode = options.DEV_MODE

    id = default(UUID)
    data = default(ImpRequest, items=[default(Import, id=id, parentId=None)])
    model = {**json.loads(data.items[0].json()),
             "date": serialize_datetime(data.updateDate), "children": None}

    options.DEV_MODE = True
    with generate_client() as client:
        response = client.cleanup_database()
        assert response.status_code == 200

        response = client.imports(data.json())
        assert response.status_code == 200

        response = client.cleanup_database()
        assert response.status_code == 200

        response = client.nodes(id)
        assert response.status_code == 404
        assert response.json() == ERROR_404

    options.DEV_MODE = False
    with generate_client() as client:
        response = client.cleanup_database()
        assert response.status_code == 200

        response = client.imports(data.json())
        assert response.status_code == 200

        response = client.cleanup_database()
        assert response.status_code == 200

        response = client.nodes(id)
        assert response.status_code == 200
        ShopUnit(**response.json())  # no ValidationError
        assert response.json() == model

    options.DEV_MODE = original_mode


def test_unrelated(client: Client):
    id1, id2 = default(UUID), default(UUID)
    data = default(ImpRequest, items=[
        default(Import, id=id1, parentId=None),
        default(Import, id=id2, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.cleanup_database()
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.nodes(id2)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.cleanup_database()
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.nodes(id2)
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_hierarchy(client: Client):
    id1, id2 = default(UUID), default(UUID)
    items = [
        default(Import, id=id1, parentId=None,
                type=ShopUnitType.CATEGORY, price=None),
        default(Import, id=id2, parentId=id1,
                type=ShopUnitType.OFFER)]
    items[0].price = None
    data = default(ImpRequest, items=items)
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.cleanup_database()
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 404
    assert response.json() == ERROR_404
    response = client.nodes(id2)
    assert response.status_code == 404
    assert response.json() == ERROR_404


if __name__ == "__main__":
    do_test(__file__)
