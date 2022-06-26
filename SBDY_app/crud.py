import logging
from asyncio import gather
from datetime import datetime
from math import ceil
from typing import Any, Iterable, List, Optional, Union
from uuid import UUID

from sqlalchemy.engine import Result
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from . import __name__ as mod_name
from .exceptions import NotEnoughResultsFound
from .models import ShopUnit, StatUnit
from .schemas import ShopUnitType
from .typedefs import DB, ShopUnits


logger = logging.getLogger(mod_name)


class Query:
    @classmethod
    def get_children(cls, selection: Select) -> Select:
        cte = selection.cte(recursive=True)
        cte = cte.union_all(
            select(ShopUnit).filter(ShopUnit.parentId == cte.c.id))
        return select(ShopUnit).join(cte, ShopUnit.id == cte.c.id)

    @classmethod
    def get_parents(cls, selection: Select) -> Select:
        cte = selection.cte(recursive=True)
        cte = cte.union_all(
            select(ShopUnit).filter(ShopUnit.id == cte.c.parentId))
        return select(ShopUnit).join(cte, ShopUnit.id == cte.c.id)

    @classmethod
    def shop_units(cls, ids: Optional[List[UUID]]) -> Select:
        selection = select(ShopUnit)
        if ids is None:
            return selection
        return selection.filter(ShopUnit.id.in_(ids))  # type: ignore

    @classmethod
    def shop_unit_id(cls, id: UUID) -> Select:
        return select(ShopUnit.id).filter(ShopUnit.id == id)

    @classmethod
    def shop_units_by_date(cls, start: datetime, end: datetime,
                           with_end: bool) -> Select:
        selection = cls.shop_units(None).filter(start <= ShopUnit.date)
        if with_end:
            return selection.filter(ShopUnit.date <= end)
        return selection.filter(ShopUnit.date < end)

    @classmethod
    def offers_by_date(cls, start: datetime, end: datetime,
                       with_end: bool) -> Select:
        return (cls.shop_units_by_date(start, end, with_end)
                .filter(ShopUnit.type == ShopUnitType.OFFER))

    @classmethod
    def stat_units(cls, ids: Optional[List[UUID]]) -> Select:
        selection = select(StatUnit)
        if ids is None:
            return selection
        return selection.filter(StatUnit.id.in_(ids))  # type: ignore

    @classmethod
    def stat_units_by_date(cls, ids: Optional[List[UUID]], start: datetime,
                           end: datetime, with_end: bool) -> Select:
        selection = cls.stat_units(ids).filter(start <= StatUnit.date)
        if with_end:
            return selection.filter(StatUnit.date <= end)
        return selection.filter(StatUnit.date < end)


### helpers ###

def assemble_shop_units(fetched: List[ShopUnit], *,
                        add_children: bool) -> ShopUnits:
    units: ShopUnits = {}

    for unit in fetched:
        ex = units.get(unit.id, None)
        if ex is None:
            # new
            unit.children = []
            units[unit.id] = unit
        elif ex is unit:
            # duplicate of existing, not a big deal
            pass
        else:
            # other unit with the same id as existing
            logger.error(
                f"Multiple results were found in the 'fetched': {unit}")
            raise MultipleResultsFound(
                "Multiple rows were found when one or none was required")

    if not add_children:
        return units

    for unit in units.values():
        parent = units.get(unit.parentId, None)  # type: ignore
        if parent is not None:
            parent.children.append(unit)

    return units


def one(units: ShopUnits, id: UUID) -> ShopUnits:
    if id in units:
        return units
    logger.error(f"No result found: {id} not in {units}")
    raise NoResultFound(
        "No row was found when one was required")


def one_or_none(units: ShopUnits, id: UUID) -> Optional[ShopUnits]:
    if id in units:
        return units
    return None


def several(units: ShopUnits, ids: Iterable[UUID]) -> ShopUnits:
    # units.keys().__rsub__ will handle it all
    logger.error(
        f"Some ids were not found, intersection: {ids - units.keys()}")
    if len(ids - units.keys()) != 0:
        raise NotEnoughResultsFound
    return units


### CRUD itself ###

async def fetch_all(db: DB, selection: Select) -> List[Any]:
    result: Result = await db.execute(selection)
    return result.scalars().all()


async def fetch_shop_units(db: DB, selection: Select, *,
                           get_children: bool = False,
                           get_parents: bool = False) -> ShopUnits:
    if get_children and get_parents:
        raise ValueError(
            "'get_parents' and 'get_children' are mutually exclusive")
    if get_children:
        selection = Query.get_children(selection)
    if get_parents:
        selection = Query.get_parents(selection)
    return assemble_shop_units(
        await fetch_all(db, selection), add_children=get_children)


async def shop_unit_exists(db: DB, id: UUID) -> bool:
    selection = Query.shop_unit_id(id)
    return len(await fetch_all(db, selection)) > 0


async def shop_unit(db: DB, id: UUID, *,
                    recursive: bool = True) -> Optional[ShopUnits]:
    selection = Query.shop_units([id])
    units = await fetch_shop_units(db, selection, get_children=recursive)
    return one_or_none(units, id)


async def shop_units(db: DB, ids: Iterable[UUID], *,
                     recursive: bool = False) -> ShopUnits:
    selection = Query.shop_units(list(ids))
    return await fetch_shop_units(db, selection, get_children=recursive)


async def offers_by_date(db: DB, start: datetime, end: datetime, *,
                         with_end: bool = True,
                         recursive: bool = False) -> ShopUnits:
    selection = Query.offers_by_date(start, end, with_end)
    return await fetch_shop_units(db, selection, get_children=recursive)


async def shop_unit_parents(db: DB, parent_id: UUID) -> ShopUnits:
    selection = Query.shop_units([parent_id])
    units = await fetch_shop_units(db, selection, get_parents=True)
    return one(units, parent_id)


async def shop_units_parents(db: DB, parent_ids: Iterable[UUID]) -> ShopUnits:
    selection = Query.shop_units(list(parent_ids))
    units = await fetch_shop_units(db, selection, get_parents=True)
    return units


async def stat_units(db: DB, id: UUID) -> List[StatUnit]:
    selection = Query.shop_units([id])
    return await fetch_all(db, selection)


async def stat_units_by_date(db: DB, id: UUID, start: datetime, end: datetime,
                             *, with_end: bool = False) -> List[StatUnit]:
    selection = Query.stat_units_by_date([id], start, end, with_end)
    return await fetch_all(db, selection)


def create_shop_unit(db: DB, /, *args: Any, **kwargs: Any) -> ShopUnit:
    unit = ShopUnit(*args, **kwargs)
    unit.children = []
    db.add(unit)
    return unit


def create_stat_unit(db: DB, shop_unit: ShopUnit) -> StatUnit:
    attrs = {name: getattr(shop_unit, name)
             for name in StatUnit._fields(exclude={"_unique_id"})}
    if shop_unit.sub_offers_count != 0:
        attrs["price"] = ceil(shop_unit.price / shop_unit.sub_offers_count)
    unit = StatUnit(**attrs)
    db.add(unit)
    return unit


async def delete_units(db: DB,
                       units: Iterable[Union[ShopUnit, ShopUnit]]) -> None:
    tasks = [db.delete(unit) for unit in units]
    await gather(*tasks)
    await db.flush()
