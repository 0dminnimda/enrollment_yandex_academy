from asyncio import gather
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Set
from uuid import UUID

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import set_committed_value
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Select

from .exceptions import NotEnoughResultsFound
from .models import ShopUnit
from .schemas import ShopUnitType
from .typedefs import DB


class Querier:
    @classmethod
    def stack_inload(cls, depth: int) -> Load:
        if depth == 1:
            return selectinload(ShopUnit.children)
        elif depth < 1:
            raise ValueError("'depth' should be >= 1")
        return cls.stack_inload(depth - 1).selectinload(ShopUnit.children)

    @classmethod
    def get_children(cls, sel: Select, depth: int) -> Select:
        """
        Recursively get children for the given selection,
        if `depth` of the recursion is negative, then there's no limit,
        if it's positive, then the defined depth is the max,
        don't make it too large, it will make everything very slow
        SEE: github.com/sqlalchemy/sqlalchemy/issues/8126
        """

        if depth == 0:
            return sel
        if depth > 0:
            return sel.options(cls.stack_inload(depth))

        cte = sel.cte(recursive=True)
        cte = cte.union_all(
            select(ShopUnit).filter(ShopUnit.parentId == cte.c.id))
        return select(ShopUnit).join(cte, ShopUnit.id == cte.c.id)

    @classmethod
    def shop_units(cls, ids: Optional[List[UUID]]) -> Select:
        sel = select(ShopUnit)
        if ids is None:
            return sel
        return sel.filter(ShopUnit.id.in_(ids))  # type: ignore

    @classmethod
    def shop_units_by_date(cls, start: datetime, end: datetime,
                           with_end: bool) -> Select:
        sel = cls.shop_units(None).filter(start <= ShopUnit.date)
        if with_end:
            return sel.filter(ShopUnit.date <= end)
        return sel.filter(ShopUnit.date < end)

    @classmethod
    def offers_by_date(cls, start: datetime, end: datetime,
                       with_end: bool) -> Select:
        return (cls.shop_units_by_date(start, end, with_end)
                .filter(ShopUnit.type == ShopUnitType.OFFER))


### helpers ###

def assemble_shop_units(in_units: List[ShopUnit]) -> List[ShopUnit]:
    units: Dict[UUID, ShopUnit] = {}
    for unit in in_units:
        set_committed_value(unit, "children", [])
        units[unit.id] = unit

    top_ids: Set[UUID] = set(units.keys())
    for unit in units.values():
        parent = units.get(unit.parentId, None)  # type: ignore
        if parent is not None:
            top_ids.remove(unit.id)
            parent.children.append(unit)

    return [units[id] for id in top_ids]


def one(units: List[ShopUnit]) -> ShopUnit:
    if len(units) == 1:
        return units[0]
    if len(units) == 0:
        raise NoResultFound(
            "No row was found when one was required")
    raise MultipleResultsFound(
        "Multiple rows were found when exactly one was required")


def one_or_none(units: List[ShopUnit]) -> Optional[ShopUnit]:
    if len(units) == 1:
        return units[0]
    if len(units) == 0:
        return None
    raise MultipleResultsFound(
        "Multiple rows were found when exactly one or none was required")


### CRUD itself ###

async def shop_unit(db: DB, id: UUID,
                    depth: int = -1) -> Optional[ShopUnit]:
    sel = Querier.shop_units([id])
    q = await db.execute(Querier.get_children(sel, depth))
    return one_or_none(assemble_shop_units(q.scalars().all()))


async def shop_units(db: DB, ids: List[UUID],
                     depth: int = 0) -> List[ShopUnit]:
    sel = Querier.shop_units(ids)
    q = await db.execute(Querier.get_children(sel, depth))
    return assemble_shop_units(q.scalars().all())


async def offers_by_date(
    db: DB, start: datetime, end: datetime,
    with_end: bool = True, depth: int = 0
) -> List[ShopUnit]:
    sel = Querier.offers_by_date(start, end, with_end)
    q = await db.execute(Querier.get_children(sel, depth))
    return assemble_shop_units(q.scalars().all())


async def shop_unit_parent(db: DB, parent_id: UUID,
                           depth: int = 0) -> ShopUnit:
    sel = Querier.shop_units([parent_id])
    q = await db.execute(Querier.get_children(sel, depth))
    return one(assemble_shop_units(q.scalars().all()))


async def shop_units_parents(db: DB, parent_ids: List[UUID],
                             depth: int = 0) -> List[ShopUnit]:
    sel = Querier.shop_units(parent_ids)
    q = await db.execute(Querier.get_children(sel, depth))
    result = assemble_shop_units(q.scalars().all())
    if len(result) != len(parent_ids):
        raise NotEnoughResultsFound
    return result
    # is this slower?
    # tasks = [self.shop_unit_parent(db, id, depth) for id in parent_ids]
    # return await gather(*tasks)  # type: ignore


# XXX: having parent cte (+ backref?) is a better idea
async def all_shop_unit_parents(
    db: DB, parent_id: Optional[UUID],
    results: Dict[UUID, ShopUnit], depth: int = 0
) -> None:

    if parent_id is None:
        return None

    if parent_id in results:
        return None
    # XXX: early key claiming, so others would not try making a db query
    results[parent_id] = None  # type: ignore

    it = await shop_unit_parent(db, parent_id, depth)
    results[parent_id] = it

    await all_shop_unit_parents(db, it.parentId, results, depth)


async def all_shop_units_parents(
    db: DB, parent_ids: Iterable[Optional[UUID]],
    results: Dict[UUID, ShopUnit], depth: int = 0
) -> Dict[UUID, ShopUnit]:

    tasks = [all_shop_unit_parents(db, id, results, depth)
             for id in parent_ids]
    await gather(*tasks)
    return results


async def update_shop_units(
    db: DB, units: Iterable[ShopUnit]
) -> List[ShopUnit]:

    # is make_transient_to_detached useful?
    tasks = [db.merge(unit) for unit in units]
    result = await gather(*tasks)
    await db.flush()
    return result  # type: ignore


async def delete_shop_unit(db: DB, unit: ShopUnit) -> None:
    await db.delete(unit)
    await db.flush()
