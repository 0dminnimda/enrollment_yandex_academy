import json
from uuid import UUID

from SBDY_app import options
from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, ShopUnit, ShopUnitType

from utils import (ERROR_404, PROFILE, Client, client, default, do_test,
                   generate_client, setup)

setup()


def test_persistency():
    if PROFILE:
        return

    original_mode = options.DEV_MODE

    id = default(UUID)
    data = default(ImpRequest, items=[default(Import, id=id, parentId=None)])
    model = {**json.loads(data.items[0].json()),
             "date": serialize_datetime(data.updateDate), "children": None}

    options.DEV_MODE = True
    with generate_client() as client:
        response = client.imports(data.json())
        assert response.status_code == 200

    options.DEV_MODE = True
    with generate_client() as client:
        response = client.nodes(id)
        assert response.status_code == 404
        assert response.json() == ERROR_404

    options.DEV_MODE = False
    with generate_client() as client:
        response = client.imports(data.json())
        assert response.status_code == 200

    options.DEV_MODE = False
    with generate_client() as client:
        response = client.nodes(id)
        assert response.status_code == 200
        ShopUnit(**response.json())  # no ValidationError
        assert response.json() == model

    options.DEV_MODE = original_mode


def test_nested(client: Client):
    ids: list = []
    for _ in range(75):
        while 1:
            id = default(UUID)
            if id not in ids:
                ids.append(id)
                break

    children = None
    data = default(ImpRequest, items=[])
    date = serialize_datetime(data.updateDate)

    for id, parent_id in zip(ids, ids[1:] + [None]):
        tp = ShopUnitType.CATEGORY if children else ShopUnitType.OFFER
        price = None if children else 69
        imp = default(Import, id=id, parentId=parent_id, type=tp, price=price)
        imp.price = price
        children = [{**json.loads(imp.json()), "price": 69,
                     "date": date, "children": children}]
        data.items.append(imp)
    assert isinstance(children, list)

    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(ids[-1])
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == children[0]

    response = client.delete(ids[-1])
    assert response.status_code == 200

    response = client.nodes(ids[-1])
    assert response.status_code == 404
    assert response.json() == ERROR_404


if __name__ == "__main__":
    do_test(__file__)
