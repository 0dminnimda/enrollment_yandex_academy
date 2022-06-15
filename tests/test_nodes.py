import json
from uuid import UUID

from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, ShopUnit, ShopUnitType

from utils import ERROR_400, ERROR_404, Client, client, default, do_test, setup

setup()


def test_unit(client: Client):
    id = default(UUID)
    data = default(ImpRequest, items=[default(Import, id=id, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    model = {**json.loads(data.items[0].json()),
             "date": serialize_datetime(data.updateDate), "children": None}

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model


def test_empty_category(client: Client):
    id = default(UUID)
    data = default(ImpRequest, items=[default(
        Import, id=id, parentId=None, type=ShopUnitType.CATEGORY, price=None)])
    data.items[0].price = None
    response = client.imports(data.json())
    assert response.status_code == 200

    model = {**json.loads(data.items[0].json()),
             "date": serialize_datetime(data.updateDate), "children": []}

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model


def test_full_category(client: Client):
    id = default(UUID)
    items = [
        default(Import, id=id, parentId=None,
                type=ShopUnitType.CATEGORY, price=None),
        default(Import, parentId=id,
                type=ShopUnitType.OFFER, price=0),
        default(Import, parentId=id,
                type=ShopUnitType.OFFER, price=0)]
    items[0].price = None
    data = default(ImpRequest, items=items)
    response = client.imports(data.json())
    assert response.status_code == 200

    date = serialize_datetime(data.updateDate)
    model = {**json.loads(items[0].json()), "date": date, "children": [
        {**json.loads(items[1].json()), "date": date, "children": None},
        {**json.loads(items[2].json()), "date": date, "children": None},
    ], "price": 0}

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model

    response = client.nodes(id)
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == model


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

    response = client.nodes(ids[-1])
    assert response.status_code == 200
    ShopUnit(**response.json())  # no ValidationError
    assert response.json() == children[0]


def test_nonexisting_items(client: Client):
    response = client.nodes(default(UUID))
    assert response.status_code == 404
    assert response.json() == ERROR_404

    response = client.nodes(default(UUID))
    assert response.status_code == 404
    assert response.json() == ERROR_404


def test_validation(client: Client):
    response = client.nodes("abooba")
    assert response.status_code == 400
    assert response.json() == ERROR_400

    response = client.nodes("42069")
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
