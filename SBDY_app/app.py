from datetime import datetime
from math import ceil
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI

from .crud import crud
from .datebase import db_injection, db_shutdown, db_startup
from .docs import info, paths
from .exceptions import ItemNotFound, ValidationFailed, add_exception_handlers
from .models import ShopUnit as DBShopUnit
from .schemas import Error, ImpRequest, Import, ShopUnit, ShopUnitType, StatResponse
from .typedefs import DB, T, AnyCallable


def path_with_docs(decorator: AnyCallable, path: str, **kw) -> AnyCallable:
    docs = paths[path][decorator.__name__]

    docs.pop("requestBody", None)
    docs.pop("parameters", None)

    for code, info in docs["responses"].items():
        if code == "400":
            info["model"] = Error

    # https://github.com/tiangolo/fastapi/issues/227
    # https://github.com/tiangolo/fastapi/issues/3650
    # https://github.com/tiangolo/fastapi/issues/2455
    # https://github.com/tiangolo/fastapi/issues/1376
    docs["responses"]["422"] = {"description": "Never appears"}

    return decorator(path, **docs, **kw)


app = FastAPI(**info)
add_exception_handlers(app)


@app.on_event("startup")
async def startup():
    await db_startup()


@app.on_event("shutdown")
async def shutdown():
    await db_shutdown()


def update_parents(parents: Dict[UUID, DBShopUnit],
                   parent_id: Optional[UUID],
                   diff: int, count: int = 0) -> None:
    if parent_id is None:
        return

    parent = parents[parent_id]
    if parent.price is None:
        parent.price = 0
    parent.price += diff
    parent.sub_offers_count += count

    update_parents(parents, parent.parentId, diff, count)


def setattrs(o: T, attrs: Dict[str, Any]) -> T:
    for name, value in attrs.items():
        setattr(o, name, value)
    return o


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest, db: DB = db_injection) -> str:
    kw = dict(date=req.updateDate, sub_offers_count=0)
    items = {imp.id: imp for imp in req.items}

    # add existing units
    # validate type (no changes allowed)
    units: Dict[UUID, DBShopUnit] = {}
    for unit in await crud.shop_units(db, list(items.keys())):
        if items[unit.id].type != unit.type:
            raise ValidationFailed
        units[unit.id] = unit

    parent_ids = {u.parentId for u in units.values() if u.parentId}
    parent_ids |= {i.parentId for i in items.values() if i.parentId}

    # add existing parents
    parents: Dict[UUID, DBShopUnit] = {}
    for parent in await crud.shop_units(db, list(parent_ids)):
        parents[parent.id] = parent

    # add parents from req
    for id in parent_ids:
        parent = parents.get(id, None)  # type: ignore
        imp_parent = items.get(id, None)  # type: ignore

        if parent is not None and imp_parent is not None:
            # change in db
            parents[id] = setattrs(parent, imp_parent.dict(exclude={"price"}))
        elif parent is None and imp_parent is not None:
            # new
            parents[id] = DBShopUnit(**kw, **imp_parent.dict())
        elif parent is None and imp_parent is None:
            # non-existent
            raise ValidationFailed
        else:
            # exists in db
            pass

    # validate parent type (can only be a category)
    for parent in parents.values():
        if parent.type != ShopUnitType.CATEGORY:
            raise ValidationFailed

    # ids_of_parents_in_db: List[UUID] = []
    # for imp in items.values():
    #     if imp.parentId is None:
    #         continue

    #     req_parent = items.get(imp.parentId, None)
    #     if req_parent is None:
    #         ids_of_parents_in_db.append(imp.parentId)
    #     else:
    #         parents[req_parent.id] = DBShopUnit(**kw, **req_parent.dict())

    # # validate parent type inside of req (can only be a category)
    # ids_of_parents_in_db: List[UUID] = []
    # validated_parents: Dict[UUID, Import] = {}
    # for imp in items.values():
    #     if imp.parentId is None:
    #         continue

    #     req_parent = items.get(imp.parentId, None)
    #     if req_parent is None:
    #         ids_of_parents_in_db.append(imp.parentId)
    #     elif req_parent.type != ShopUnitType.CATEGORY:
    #         raise ValidationFailed
    #     else:
    #         validated_parents[req_parent.id] = req_parent

    # parents: Dict[UUID, DBShopUnit] = {}

    # # add validated parents
    # for id, req_parent in validated_parents.items():
    #     parent = units.get(id, None)
    #     if parent is None:
    #         parent = await crud.shop_unit_parent(db, id)
    #     parents[id] = parent

    # # add parents from req
    # ids_of_parents_in_db: List[UUID] = []
    # parents: Dict[UUID, DBShopUnit] = {}
    # for imp in items.values():
    #     if imp.parentId is None:
    #         continue

    #     parent = items.get(imp.parentId, None)
    #     if parent is None:
    #         ids_of_parents_in_db.append(imp.parentId)
    #     elif parent.type != ShopUnitType.CATEGORY:
    #         raise ValidationFailed
    #     elif parent.id in units:
    #         db_parent = units[parent.id]
    #         parents[parent.id] = db_parent
    #         if db_parent.parentId
    #     else:
    #         parents[parent.id] = DBShopUnit(**kw, **parent.dict())

    # # validate parent type (can only be a category)
    # # add first parents from db
    # for parent_id in ids_of_parents_in_db:
    #     parent = await crud.shop_unit_parent(db, parent_id)
    #     if parent.type != ShopUnitType.CATEGORY:
    #         raise ValidationFailed
    #     parents[parent.id] = parent

    # add all remaining parents higher up in the hierarchy
    await crud.all_shop_units_parents(
        db, (p.parentId for p in parents.values()), parents)

    # update parents's date
    for parent in parents.values():
        parent.date = req.updateDate

    # # update parents of existing offers
    # offers: Dict[UUID, Import] = {}
    # for id, unit in units.items():
    #     imp = items[id]
    #     if unit.type == ShopUnitType.OFFER:
    #         assert imp.price is not None
    #         assert unit.price is not None
    #         update_parents(parents, unit.parentId, imp.price - unit.price)
    #         offers[id] = imp

    # # update parents of new offers
    # for id in items.keys() - units.keys():
    #     imp = items[id]
    #     if imp.type == ShopUnitType.OFFER:
    #         assert imp.price is not None
    #         update_parents(parents, imp.parentId, imp.price)
    #         offers[id] = imp

    offers: Dict[UUID, Import] = {id: imp for id, imp in items.items()
                                  if imp.type == ShopUnitType.OFFER}

    # update parents of offers
    for id, imp in offers.items():
        assert imp.price is not None

        unit = units.get(id, None)  # type: ignore
        if unit is None:
            update_parents(parents, imp.parentId, imp.price, count=1)
            continue
        assert unit.price is not None

        if unit.parentId == imp.parentId:
            update_parents(parents, imp.parentId, imp.price - unit.price)
        else:
            update_parents(parents, imp.parentId, imp.price, count=1)
            update_parents(parents, unit.parentId, -unit.price, count=-1)

    # update parents
    await crud.update_shop_units(db, parents.values())

    # update offers
    await crud.update_shop_units(
        db, (DBShopUnit(**kw, **imp.dict()) for imp in offers.values()))

    # update the rest of the categories
    categories: List[DBShopUnit] = []
    for id in items.keys() - parents.keys() - offers.keys():
        imp = items[id]
        assert imp.type == ShopUnitType.CATEGORY

        unit = parents.get(id, None)  # type: ignore
        if unit is None:
            categories.append(DBShopUnit(**kw, **imp.dict()))
            continue

        categories.append(setattrs(unit, imp.dict(exclude={"price"})))

    # update categories
    await crud.update_shop_units(db, categories)

    return "Successful import"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID) -> str:
    return "Not implemented yet"


def sum_to_mean(unit: DBShopUnit) -> None:
    # usually if price is None, unit is an empty category, so whatever
    if unit.price is not None and unit.sub_offers_count != 0:
        unit.price = ceil(unit.price / unit.sub_offers_count)

    for unit in unit.children:
        sum_to_mean(unit)


@path_with_docs(app.get, "/nodes/{id}", response_model=ShopUnit)
async def nodes(id: UUID, db: DB = db_injection):
    unit = await crud.shop_unit(db, id)
    if unit is None:
        raise ItemNotFound

    sum_to_mean(unit)
    return unit


@path_with_docs(app.get, "/sales", response_model=StatResponse)
async def sales(date: datetime) -> StatResponse:
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic", response_model=StatResponse)
async def node_statistic(id: UUID,
                         dateStart: datetime = datetime.min,
                         dateEnd: datetime = datetime.max) -> StatResponse:
    return "Not implemented yet"
