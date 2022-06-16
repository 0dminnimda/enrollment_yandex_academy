from asyncio import gather
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Set
from uuid import UUID

from sqlalchemy.engine import Result
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.orm.attributes import set_committed_value
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Executable, Select

from .exceptions import NotEnoughResultsFound
from .models import ShopUnit
from .schemas import ShopUnitType
from .typedefs import DB

# Depth, 

class Querier:
    @classmethod
    def stack_inload(cls, depth: int) -> Load:
        if depth == 1:
            return selectinload(ShopUnit.children)
        elif depth < 1:
            raise ValueError("'depth' should be >= 1")
        return cls.stack_inload(depth - 1).selectinload(ShopUnit.children)

    # we need that depth because of async recursive ShopUnit
    # SEE: github.com/sqlalchemy/sqlalchemy/issues/8126
    @classmethod
    def get_children(cls, sel: Select, depth: int) -> Executable:
        if depth == 0:
            return sel
        if depth > 0:
            return sel.options(cls.stack_inload(depth))

        # print("dis")
        # sel = sel.cte("cte", recursive=True)
        # bottom = select(ShopUnit).join(sel, ShopUnit.parentId == sel.c.id)
        # return bottom# sel.union(bottom)


        # tree = sel.cte(name='tree', recursive=True)

        # parent = aliased(tree, name='p')
        # children = aliased(ShopUnit, name='c')
        # tree = tree.union_all(
        #     select(children)
        #     .filter(children.parentId == parent.c.id))


        cte = sel.cte(recursive=True)
        cte = cte.union_all(
            select(ShopUnit).filter(ShopUnit.parentId == cte.c.id))
        return select(ShopUnit).join(cte, ShopUnit.id == cte.c.id)
        # result_nodes = await session.execute()


        # top_query = (
        #     db.session.query(NodeParentRelation.child_id, NodeParentRelation.parent_id)
        #     .filter(NodeParentRelation.child_id == 1)
        #     .cte(recursive=True))

        # parents = db.aliased(top_query)
        # t = db.aliased(NodeParentRelation)

        # query = top_query.union_all(
        #     db.session.query(t.child_id, t.parent_id).
        #         join(parents, t.child_id == parents.c.parent_id))


        # # included_parts = (
        # #     select(parts.c.sub_part, parts.c.part, parts.c.quantity)
        # #     .where(parts.c.part=='our part')
        # #     .cte(recursive=True))
        # included_parts = sel.cte(recursive=True)

        # incl_alias = included_parts.alias()
        # # parts_alias = parts.alias()

        # # included_parts = included_parts.union_all(
        # #     select(parts_alias.c.sub_part, parts_alias.c.part, parts_alias.c.quantity)
        # #     .where(parts_alias.c.part==incl_alias.c.sub_part))
        # included_parts = included_parts.union_all(
        #     select(ShopUnit)
        #     .where(ShopUnit.id == incl_alias.c.parentId))

        # # statement = (
        # #     select(
        # #         included_parts.c.sub_part,
        # #         func.sum(included_parts.c.quantity).label('total_quantity'))
        # #     .group_by(included_parts.c.sub_part))
        # statement = (
        #     select(included_parts.c.parentId)
        #     .group_by(included_parts.c.parentId))

        # return statement

    @classmethod
    def shop_units(cls, ids: Optional[List[UUID]]) -> Select:
        sel = select(ShopUnit)
        if sel is not None:
            return sel.filter(ShopUnit.id.in_(ids))  # type: ignore
        return sel

    # @classmethod
    # def shop_units_with_children(cls, ids: Optional[List[UUID]], depth: int) -> Executable:
    #     top = select(ShopUnit)
    #     if ids is not None:
    #         top = top.filter(ShopUnit.id.in_(ids))  # type: ignore

    #     if depth == 0:
    #         return top
    #     if depth > 0:
    #         return top.options(cls.stack_inload(depth))

    #     Select.cte

    #     top = top.cte("cte", recursive=True)
    #     bottom = select(ShopUnit).join(top, ShopUnit.parentId == top.c.id)
    #     return top.union(bottom)

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


class CRUD:
    # depth: int
    # selectinload: Load

    # def reset(self, depth: int) -> None:
    #     self.depth = depth
    #     self.selection = stack_selectinload(depth)

    # async def startup(self, db: DB, depth: int = 200) -> None:
    #     q = await db.execute(select(Depth))
    #     db_depth = q.scalars().one_or_none()

    #     if db_depth is not None:
    #         depth = db_depth.depth

    #     self.reset(depth)

    # async def shutdown(self, db: DB) -> None:
    #     await db.merge(Depth(id=1, depth=self.depth))

    # def select_all_shop_units(self, depth: int) -> Select:
    #     if depth == 0:
    #         return select(ShopUnit)
    #     if depth < 0:
    #         return select(ShopUnit).options(self.selection)
    #     return select(ShopUnit).options(stack_selectinload(depth))

    # def select_shop_unit(self, id: UUID, depth: int) -> Select:
    #     return self.select_all_shop_units(depth).filter(ShopUnit.id == id)

    async def shop_unit(self, db: DB, id: UUID,
                        depth: int = -1) -> Optional[ShopUnit]:
        sel = Querier.shop_units([id])
        q = await db.execute(Querier.get_children(sel, depth))
        return one_or_none(assemble_shop_units(q.scalars().all()))
        # print([(p.id, p.parentId) for p in al])
        return q.scalars().one_or_none()

    # def select_shop_units(self, ids: List[UUID], depth: int) -> Select:
    #     return (self.select_all_shop_units(depth)
    #             .filter(ShopUnit.id.in_(ids)))  # type: ignore

    async def shop_units(self, db: DB, ids: List[UUID],
                         depth: int = 0) -> List[ShopUnit]:
        sel = Querier.shop_units(ids)
        q = await db.execute(Querier.get_children(sel, depth))
        return assemble_shop_units(q.scalars().all())
        return q.scalars().all()

    # def select_shop_units_by_date(self, start: datetime, end: datetime,
    #                               with_end: bool, depth: int) -> Select:
    #     s = self.select_all_shop_units(depth).filter(start <= ShopUnit.date)
    #     if with_end:
    #         return s.filter(ShopUnit.date <= end)
    #     return s.filter(ShopUnit.date < end)

    # def select_offers_by_date(self, start: datetime, end: datetime,
    #                           with_end: bool, depth: int) -> Select:
    #     return (self.select_shop_units_by_date(start, end, with_end, depth)
    #             .filter(ShopUnit.type == ShopUnitType.OFFER))

    async def offers_by_date(
        self, db: DB, start: datetime, end: datetime,
        with_end: bool = True, depth: int = 0
    ) -> List[ShopUnit]:
        sel = Querier.offers_by_date(start, end, with_end)
        q = await db.execute(Querier.get_children(sel, depth))
        return assemble_shop_units(q.scalars().all())
        # return q.scalars().all()

    async def shop_unit_parent(self, db: DB, parent_id: UUID,
                               depth: int = 0) -> ShopUnit:
        sel = Querier.shop_units([parent_id])
        q = await db.execute(Querier.get_children(sel, depth))
        return one(assemble_shop_units(q.scalars().all()))
        return q.scalars().one()

    async def shop_units_parents(self, db: DB, parent_ids: List[UUID],
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

    # XXX: having parent backref + selectinload probably is better idea
    async def all_shop_unit_parents(
        self, db: DB, parent_id: Optional[UUID],
        results: Dict[UUID, ShopUnit], depth: int = 0
    ) -> None:

        if parent_id is None:
            return None

        if parent_id in results:
            return None
        # XXX: early key claiming, so others would not try making a db query
        results[parent_id] = None  # type: ignore

        it = await self.shop_unit_parent(db, parent_id, depth)
        results[parent_id] = it

        await self.all_shop_unit_parents(db, it.parentId, results, depth)

    async def all_shop_units_parents(
        self, db: DB, parent_ids: Iterable[Optional[UUID]],
        results: Dict[UUID, ShopUnit], depth: int = 0
    ) -> Dict[UUID, ShopUnit]:

        tasks = [self.all_shop_unit_parents(db, id, results, depth)
                 for id in parent_ids]
        await gather(*tasks)
        return results

    async def update_shop_units(
        self, db: DB, units: Iterable[ShopUnit]
    ) -> List[ShopUnit]:

        # is make_transient_to_detached useful?
        tasks = [db.merge(unit) for unit in units]
        result = await gather(*tasks)
        await db.flush()
        return result  # type: ignore

    async def delete_shop_unit(self, db: DB, unit: ShopUnit) -> None:
        await db.delete(unit)
        await db.flush()


crud = CRUD()
