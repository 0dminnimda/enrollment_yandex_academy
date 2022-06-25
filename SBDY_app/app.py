import logging
from datetime import datetime, timedelta
from math import ceil
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import FastAPI

from . import __name__ as mod_name
from . import crud, models
from .database import db_injection, db_shutdown, db_startup
from .docs import info, paths
from .exceptions import ItemNotFound, ValidationFailed, add_exception_handlers
from .schemas import (Error, Import, ImpRequest, ShopUnit, ShopUnitType,
                      StatResponse)
from .typedefs import DB, AnyCallable, ShopUnits, T


logger = logging.getLogger(mod_name)


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


def update_parents(parents: ShopUnits,
                   parent_id: Optional[UUID],
                   diff: int, count: int = 0) -> None:
    if parent_id is None:
        return

    parent = parents[parent_id]
    parent.price += diff
    parent.sub_offers_count += count

    update_parents(parents, parent.parentId, diff, count)


def setattrs(o: T, attrs: Dict[str, Any]) -> T:
    for name, value in attrs.items():
        setattr(o, name, value)
    return o


def recorded_update_unit(
    db: DB, date: datetime, imp: Import,
    unit: Optional[models.ShopUnit], *,
    _kw: dict = {"date": None, "sub_offers_count": 0}
) -> models.ShopUnit:

    _kw["date"] = date
    if unit is None:
        # new
        return crud.create_shop_unit(db, **_kw, **imp.dict())
    elif unit.type == ShopUnitType.CATEGORY:
        # change in db
        return setattrs(unit, imp.dict(exclude={"price"}))
    elif unit.type == ShopUnitType.OFFER:
        # change in db
        return setattrs(unit, {**_kw, **imp.dict()})
    raise ValueError(f"Unknown unit type: {unit.type}")


"""
parent = parents.get(id, None)  # type: ignore
if parent is None:
    # new
    parents[id] = crud.create_shop_unit(db, **kw, **imp.dict())
else:
    # change in db
    parents[id] = setattrs(parent, imp.dict(exclude={"price"}))


offer = units.get(id, None)  # type: ignore
if offer is None:
    crud.create_shop_unit(db, **kw, **imp.dict())
else:
    setattrs(offer, {**kw, **imp.dict()})


unit = units.get(id, None)  # type: ignore
if unit is None:
    crud.create_shop_unit(db, **kw, **imp.dict())
else:
    setattrs(unit, imp.dict(exclude={"price"}))
"""


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest, db: DB = db_injection) -> str:
    items = {imp.id: imp for imp in req.items}
    units = await crud.shop_units(db, items.keys())

    # validate type (no changes allowed)
    for id, unit in units.items():
        if items[unit.id].type != unit.type:
            logger.error(f"Type change of {unit.id}:"
                         f" {items[unit.id].type} != {unit.type}")
            raise ValidationFailed

    possible_parent_ids = {u.parentId for u in units.values() if u.parentId}
    possible_parent_ids |= {i.parentId for i in items.values() if i.parentId}

    parents = await crud.shop_units_parents(db, possible_parent_ids)

    # add parents from the import request
    kw = dict(date=req.updateDate, sub_offers_count=0)
    for id in possible_parent_ids:
        parent = parents.get(id, None)  # type: ignore
        imp_parent = items.get(id, None)  # type: ignore

        # if parent is not None and imp_parent is not None:
        #     # change in db
        #     parents[id] = setattrs(parent, imp_parent.dict(exclude={"price"}))
        # elif parent is None and imp_parent is not None:
        #     # new
        #     parents[id] = crud.create_shop_unit(db, **kw, **imp_parent.dict())
        # elif parent is None and imp_parent is None:
        #     # non-existent
        #     logger.error(f"Non-existent {id}")
        #     raise ValidationFailed
        # else:
        #     # present in db, no change
        #     pass
        if imp_parent is None:
            if parent is None:
                # non-existent
                logger.error(f"Non-existent {id}")
                raise ValidationFailed
            else:
                # present in db, no change
                pass
        else:
            parents[id] = recorded_update_unit(
                db, req.updateDate, imp_parent, parent)
            # if parent is None
            #     # new
            #     parents[id] = crud.create_shop_unit(db, **kw, **imp_parent.dict())
            # else:
            #     # change in db
            #     parents[id] = setattrs(parent, imp_parent.dict(exclude={"price"}))

    # validate parent's type (can only be a category)
    # and update parents's date
    for parent in parents.values():
        if parent.type != ShopUnitType.CATEGORY:
            logger.error(f"Parent {parent.id} is not a category:"
                         f" {parent.type} != {ShopUnitType.CATEGORY}")
            raise ValidationFailed
        parent.date = req.updateDate

    offers: Dict[UUID, Import] = {id: imp for id, imp in items.items()
                                  if imp.type == ShopUnitType.OFFER}

    # update parents of offers
    for id, imp in offers.items():
        assert imp.price is not None

        offer = units.get(id, None)  # type: ignore
        if offer is None:
            update_parents(parents, imp.parentId, imp.price, count=1)
            continue

        if offer.parentId == imp.parentId:
            update_parents(parents, imp.parentId, imp.price - offer.price)
        else:
            update_parents(parents, imp.parentId, imp.price, count=1)
            update_parents(parents, offer.parentId, -offer.price, count=-1)

    # update offers
    for id, imp in offers.items():
        offer = units.get(id, None)  # type: ignore
        recorded_update_unit(db, req.updateDate, imp, offer)
        # if offer is None:
        #     crud.create_shop_unit(db, **kw, **imp.dict())
        # else:
        #     setattrs(offer, {**kw, **imp.dict()})

    # update the rest of the categories
    for id in items.keys() - parents.keys() - offers.keys():
        imp = items[id]
        assert imp.type == ShopUnitType.CATEGORY

        unit = units.get(id, None)  # type: ignore
        recorded_update_unit(db, req.updateDate, imp, unit)
        # if unit is None:
        #     crud.create_shop_unit(db, **kw, **imp.dict())
        # else:
        #     setattrs(unit, imp.dict(exclude={"price"}))

    return "Successful import"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID, db: DB = db_injection) -> str:
    result = await crud.shop_unit(db, id)
    if result is None:
        raise ItemNotFound
    await crud.delete_shop_units(db, result.values())

    unit = result[id]
    if unit.parentId:
        parents = await crud.shop_unit_parents(db, unit.parentId)
        update_parents(parents, unit.parentId, -unit.price, count=-1)

    return "Successful deletion"


def shop_unit_to_schema(unit: models.ShopUnit) -> ShopUnit:
    """
    Takes price and devices it by the number of sub offers,
    then puts it into instance of ShopUnit
    """

    result = ShopUnit(**{
        **unit.__dict__,
        "children": [shop_unit_to_schema(unit) for unit in unit.children]
    })

    if unit.sub_offers_count != 0:
        result.price = ceil(unit.price / unit.sub_offers_count)

    return result


@path_with_docs(app.get, "/nodes/{id}", response_model=ShopUnit)
async def nodes(id: UUID, db: DB = db_injection) -> ShopUnit:
    result = await crud.shop_unit(db, id)
    if result is None:
        raise ItemNotFound
    return shop_unit_to_schema(result[id])


@path_with_docs(app.get, "/sales", response_model=StatResponse)
async def sales(date: datetime, db: DB = db_injection) -> StatResponse:
    units = await crud.offers_by_date(db, date - timedelta(days=1), date)
    return StatResponse(items=list(units.values()))


@path_with_docs(app.get, "/node/{id}/statistic", response_model=StatResponse)
async def statistic(id: UUID,
                    dateStart: datetime = datetime.min,
                    dateEnd: datetime = datetime.max) -> StatResponse:
    return StatResponse(items=[])
