from uuid import UUID

from SBDY_app.schemas import Import, ImpRequest, ShopUnitType

from utils import ERROR_400, Client, client, default, do_test, setup

setup()


def test_different_amounts_of_items(client: Client):
    data = default(ImpRequest, items=[])
    response = client.imports(data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    data = default(ImpRequest, items=[default(Import, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    data = default(
        ImpRequest,
        items=[default(Import, parentId=None),
               default(Import, parentId=None)])
    response = client.imports(data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same


def test_category_price(client: Client):
    id = default(UUID)
    # TODO: adding the category without children with id to the db
    # TODO: price of the category with id == None

    data = default(ImpRequest, items=[default(Import, parentId=id, price=420)])
    response = client.imports(data.json())
    assert response.status_code == 200

    # TODO: price of the category with id == 420

    data = default(ImpRequest, items=[default(Import, parentId=id, price=69)])
    response = client.imports(data.json())
    assert response.status_code == 200

    # TODO: price of the category with id == (420 + 69) / 2


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
    imp = default(Import)
    imp.type = ShopUnitType.CATEGORY
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_type_change(client: Client):
    imp = default(Import, parentId=None,
                  type=ShopUnitType.CATEGORY, price=None)
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 200

    imp.type = ShopUnitType.OFFER
    data = default(ImpRequest, items=[imp])
    response = client.imports(data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_not_required_Import_fields(client: Client):
    string = default(ImpRequest).json(exclude={"items": {0: {"parentId"}}})
    response = client.imports(string)
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    string = default(ImpRequest).json(exclude={"items": {0: {"price"}}})
    response = client.imports(string)
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same


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
