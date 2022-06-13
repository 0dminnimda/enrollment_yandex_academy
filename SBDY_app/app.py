from datetime import datetime
from math import ceil
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI

from .crud import crud
from .datebase import db_injection, db_shutdown, db_startup
from .docs import info, paths
from .exceptions import ItemNotFound, ValidationFailed, add_exception_handlers
from .models import ShopUnit as DBShopUnit
from .schemas import Error, ImpRequest, ShopUnit, ShopUnitType, StatResponse
from .typedefs import DB, AnyCallable


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
                   parent_id: Optional[UUID], diff: int) -> None:
    if parent_id is None:
        return

    parent = parents[parent_id]
    if parent.price is None:
        parent.price = 0
    parent.price += diff
    parent.sub_offers_count += 1

    update_parents(parents, parent.parentId, diff)


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest, db: DB = db_injection) -> str:
    kw = dict(date=req.updateDate, sub_offers_count=0)
    items = {imp.id: imp for imp in req.items}

    # validate type (no changes allowed)
    db_units = await crud.shop_units(db, list(items.keys()))
    for unit in db_units:
        if items[unit.id].type != unit.type:
            raise ValidationFailed

    # validate parent type (can only be a category)
    # add parents from req
    ids_of_parents_in_db: List[UUID] = []
    parents: Dict[UUID, DBShopUnit] = {}
    for imp in req.items:
        if imp.parentId is None:
            continue

        parent = items.get(imp.parentId, None)
        if parent is None:
            ids_of_parents_in_db.append(imp.parentId)
        elif parent.type != ShopUnitType.CATEGORY:
            raise ValidationFailed
        else:
            parents[parent.id] = DBShopUnit(**kw, **parent.dict())

    # validate parent type (can only be a category)
    # add first parents from db
    for parent_id in ids_of_parents_in_db:
        parent = await crud.shop_unit_parent(db, parent_id)
        if parent.type != ShopUnitType.CATEGORY:
            raise ValidationFailed
        parents[parent.id] = parent

    # add all remaining parents higher up in the hierarchy
    await crud.all_shop_units_parents(
        db, (p.parentId for p in parents.values()), parents)

    # update parents's date
    for parent in parents.values():
        parent.date = req.updateDate

    # update parents of existing units
    for unit in db_units:
        imp = items[unit.id]
        if unit.type == ShopUnitType.OFFER:
            assert imp.price is not None
            assert unit.price is not None
            update_parents(parents, unit.parentId, imp.price - unit.price)

    # update parents of new units
    for id in items.keys() - set(u.id for u in db_units):
        imp = items[id]
        if imp.type == ShopUnitType.OFFER:
            assert imp.price is not None
            update_parents(parents, imp.parentId, imp.price)

    await crud.update_shop_units(db, parents.values())

    # create new units
    new_units = items.keys() - parents.keys()
    db_units = await crud.update_shop_units(
        db, (DBShopUnit(**kw, **items[id].dict()) for id in new_units))

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
