from uuid import UUID

from fastapi.testclient import TestClient
from SBDY_app.schemas import Import, ImpRequest

from utils import ERROR_400, client, default, do_test, setup


setup()


def test_different_amounts_of_items(client: TestClient):
    data = default(ImpRequest, items=[])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    data = default(ImpRequest)
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    data = default(ImpRequest, items=[default(Import), default(Import)])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same


def test_category_price(client: TestClient):
    id = default(UUID)
    # TODO: adding the category without children with id to the db
    # TODO: price of the category with id == None

    data = default(ImpRequest, items=[default(Import, parentId=id, price=420)])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    # TODO: price of the category with id == 420

    data = default(ImpRequest, items=[default(Import, parentId=id, price=69)])
    response = client.post("/imports", data=data.json())
    assert response.status_code == 200

    # TODO: price of the category with id == (420 + 69) / 2


def test_not_unique_ids(client: TestClient):
    data = default(ImpRequest, items=[])
    data.items = [default(Import)] * 2
    response = client.post("/imports", data=data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400

    data = default(ImpRequest, items=[])
    imp = default(Import)
    data.items = [default(Import), imp, default(Import), imp, default(Import)]
    response = client.post("/imports", data=data.json())
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_not_required_Import_fields(client: TestClient):
    string = default(ImpRequest).json(exclude={"items": {0: {"parentId"}}})
    response = client.post("/imports", data=string)
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same

    string = default(ImpRequest).json(exclude={"items": {0: {"price"}}})
    response = client.post("/imports", data=string)
    assert response.status_code == 200

    # TODO: check that unit appeared in the db and is same


def test_ImpRequest_validation(client: TestClient):
    string = default(ImpRequest, items=[]).json(exclude={"items"})
    response = client.post("/imports", data=string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"updateDate"})
    response = client.post("/imports", data=string)
    assert response.status_code == 400
    assert response.json() == ERROR_400


def test_Import_validation(client: TestClient):
    string = default(ImpRequest).json(exclude={"items": {0: {"id"}}})
    response = client.post("/imports", data=string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"items": {0: {"name"}}})
    response = client.post("/imports", data=string)
    assert response.status_code == 400
    assert response.json() == ERROR_400

    string = default(ImpRequest).json(exclude={"items": {0: {"type"}}})
    response = client.post("/imports", data=string)
    assert response.status_code == 400
    assert response.json() == ERROR_400


if __name__ == "__main__":
    do_test(__file__)
