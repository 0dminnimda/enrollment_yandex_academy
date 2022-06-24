import json
from datetime import datetime
from math import ceil
from random import shuffle
from uuid import UUID

from SBDY_app.patches import serialize_datetime
from SBDY_app.schemas import Import, ImpRequest, ShopUnit, ShopUnitType

from unit_tst import IMPORT_BATCHES, ROOT_ID
from utils import ERROR_400, Client, client, default, do_test, setup

setup()


def test_different_amounts_of_items(client: Client):
    data = default(ImpRequest, items=[])
    response = client.imports(data.json())
    assert response.status_code == 200

    data = default(ImpRequest, items=[default(Import, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(data.items[0].id)
    assert response.status_code == 200
    assert response.json() == {
        **json.loads(data.items[0].json()),
        "date": serialize_datetime(data.updateDate), "children": None}

    data = default(
        ImpRequest,
        items=[default(Import, parentId=None),
               default(Import, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(data.items[0].id)
    assert response.status_code == 200
    assert response.json() == {
        **json.loads(data.items[0].json()),
        "date": serialize_datetime(data.updateDate), "children": None}

    response = client.nodes(data.items[1].id)
    assert response.status_code == 200
    assert response.json() == {
        **json.loads(data.items[1].json()),
        "date": serialize_datetime(data.updateDate), "children": None}


def test_category_price(client: Client):
    id1 = default(UUID)
    data = default(ImpRequest, items=[
        default(Import, id=id1, parentId=None,
                price=None, type=ShopUnitType.CATEGORY)])
    data.items[0].price = None
    response = client.imports(data.json())
    assert response.status_code == 200

    data = default(ImpRequest, items=[
                   default(Import, parentId=id1, price=420)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 200
    assert ShopUnit(**response.json()).price == 420

    id2 = default(UUID)
    data = default(ImpRequest, items=[default(
        Import, id=id2, parentId=id1, price=69)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 200
    assert ShopUnit(**response.json()).price == ceil((420 + 69) / 2)

    data = default(ImpRequest, items=[default(
        Import, id=id2, parentId=None, price=69)])
    response = client.imports(data.json())
    assert response.status_code == 200

    response = client.nodes(id1)
    assert response.status_code == 200
    assert ShopUnit(**response.json()).price == 420


def test_repeated_category(client: Client):
    date = serialize_datetime(default(datetime))
    batches = [{**batch, "updateDate": date} for batch in IMPORT_BATCHES]

    for batch in batches:
        response = client.imports(json.dumps(batch))
        assert response.status_code == 200

    response = client.nodes(ROOT_ID)
    assert response.status_code == 200
    result = response.json()

    shuffled = batches[:]
    shuffle(shuffled)
    for batch in batches + shuffled:
        response = client.imports(json.dumps(batch))
        assert response.status_code == 200

        response = client.nodes(ROOT_ID)
        assert response.status_code == 200
        assert response.json() == result


def test_not_unique_ids(client: Client):
    data = default(ImpRequest, items=[])
    data.items = [default(Import)] * 2
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400

    data = default(ImpRequest, items=[])
    imp = default(Import)
    data.items = [default(Import), imp, default(Import), imp, default(Import)]
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_valid_category_price(client: Client):
    imp = default(Import, parentId=None,
                  type=ShopUnitType.CATEGORY, price=None)
    imp.price = None
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp = default(Import, parentId=None,
                  type=ShopUnitType.CATEGORY, price=None)
    data = default(ImpRequest, items=[imp])
    string = data.json(exclude={"items": {0: {"price"}}})
    response = client.imports(string)
    assert response.status_code == 200


def test_invalid_category_price(client: Client):
    imp = default(Import, parentId=None)
    imp.type = ShopUnitType.CATEGORY
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_valid_offer_price(client: Client):
    imp = default(Import, parentId=None, type=ShopUnitType.OFFER)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200


def test_invalid_offer_price(client: Client):
    imp = default(Import, parentId=None, type=ShopUnitType.OFFER)
    imp.price = None
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_type_change(client: Client):
    imp = default(Import, parentId=None,
                  type=ShopUnitType.CATEGORY, price=None)
    imp.price = None
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp.type = ShopUnitType.OFFER
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_child_of_offer(client: Client):
    imp = default(Import, parentId=None,
                  type=ShopUnitType.OFFER)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp = default(Import, parentId=imp.id)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_nonexisting_parent(client: Client):
    data = default(ImpRequest, items=[default(Import)])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_change_to_nonexisting_offer_parent(client: Client):
    imp = default(Import, parentId=None, type=ShopUnitType.OFFER)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp = default(Import, type=ShopUnitType.OFFER)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_change_to_nonexisting_category_parent(client: Client):
    imp = default(Import, parentId=None, price=None,
                  type=ShopUnitType.CATEGORY)
    imp.price = None
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp1 = default(Import, price=None,
                   type=ShopUnitType.CATEGORY)
    imp1.price = None
    imp2 = default(Import, parentId=imp1.id, type=ShopUnitType.OFFER)
    data = default(ImpRequest, items=[imp1, imp2])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_not_required_Import_fields(client: Client):
    string = default(ImpRequest).json(exclude={"items": {0: {"parentId"}}})
    response = client.imports(string)
    assert response.status_code == 200

    data = default(ImpRequest, items=[
        default(Import, parentId=None,
                type=ShopUnitType.CATEGORY, price=None)])
    response = client.imports(data.json(exclude={"items": {0: {"price"}}}))
    assert response.status_code == 200


def test_ImpRequest_validation(client: Client):
    string = default(ImpRequest, items=[]).json(exclude={"items"})
    response = client.imports(string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"updateDate"})
    response = client.imports(string)
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_Import_validation(client: Client):
    string = default(ImpRequest).json(exclude={"items": {0: {"id"}}})
    response = client.imports(string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"items": {0: {"name"}}})
    response = client.imports(string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"items": {0: {"type"}}})
    response = client.imports(string)
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
