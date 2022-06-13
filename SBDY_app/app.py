from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI

from .crud import crud
from .datebase import db_injection, db_shutdown, db_startup
from .docs import info, paths
from .exceptions import ItemNotFound, ValidationFailed, add_exception_handlers
from .models import ShopUnit as DBShopUnit
from .schemas import (Error, Import, ImpRequest, ShopUnit, ShopUnitType,
                      StatResponse)
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


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest, db: DB = db_injection) -> str:
    items = {imp.id: imp for imp in req.items}

    units = await crud.shop_units(db, list(items.keys()))
    for unit in units:
        if items[unit.id].type != unit.type:
            raise ValidationFailed

    parents_in_db: List[UUID] = []
    for imp in req.items:
        if imp.parentId is None:
            continue

        parent = items.get(imp.parentId, None)
        if parent is None:
            parents_in_db.append(imp.parentId)
        elif parent.type != ShopUnitType.CATEGORY:
            raise ValidationFailed

    parents: List[DBShopUnit] = []
    for parent_id in parents_in_db:
        parent = await crud.shop_unit_parent(db, parent_id)
        if parent.type != ShopUnitType.CATEGORY:
            raise ValidationFailed
        parents.append(parent)

    parents += (await crud.all_shop_units_parents(
        db, (p.parentId for p in parents)))[0]

    for parent in parents:
        parent.date = req.updateDate

    await crud.update_shop_units(db, parents)

    kw = dict(date=req.updateDate, sub_offers_count=0)
    units = await crud.update_shop_units(
        db, (DBShopUnit(**kw, **imp.dict()) for imp in req.items))

    # for parent in parents:
    #     count = 0
    #     summation = 0
    #     for sub in parent.children:
    #         pass

    return "Successful import"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID) -> str:
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}", response_model=ShopUnit)
async def nodes(id: UUID, db: DB = db_injection):
    unit = await crud.shop_unit(db, id)
    if unit is None:
        raise ItemNotFound
    return unit


@path_with_docs(app.get, "/sales", response_model=StatResponse)
async def sales(date: datetime) -> StatResponse:
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic", response_model=StatResponse)
async def node_statistic(id: UUID,
                         dateStart: datetime = datetime.min,
                         dateEnd: datetime = datetime.max) -> StatResponse:
    return "Not implemented yet"
