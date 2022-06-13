from asyncio import gather
from typing import Iterable, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy.engine import Result
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql import Select

from .models import Depth, ShopUnit
from .typedefs import DB


def stack_selectinload(depth: int) -> Load:
    if depth == 1:
        return selectinload(ShopUnit.children)
    elif depth < 1:
        raise ValueError("'depth' should be >= 1")
    return stack_selectinload(depth - 1).selectinload(ShopUnit.children)


class CRUD:
    depth: int
    selectinload: Load

    def reset(self, depth: int) -> None:
        self.depth = depth
        self.selection = stack_selectinload(depth)

    async def startup(self, db: DB, depth: int = 150) -> None:
        q = await db.execute(select(Depth))
        db_depth = q.scalars().one_or_none()

        if db_depth is not None:
            depth = db_depth.depth

        self.reset(depth)

    async def shutdown(self, db: DB) -> None:
        await db.merge(Depth(id=1, depth=self.depth))

    def select_all_shop_units(self, depth: int) -> Select:
        if depth == 0:
            return select(ShopUnit)
        if depth < 0:
            return select(ShopUnit).options(self.selection)
        return select(ShopUnit).options(stack_selectinload(depth))

    def select_shop_unit(self, id: UUID, depth: int) -> Select:
        return self.select_all_shop_units(depth).filter(ShopUnit.id == id)

    async def shop_unit(self, db: DB, id: UUID,
                        depth: int = -1) -> Optional[ShopUnit]:
        q = await db.execute(self.select_shop_unit(id, depth))
        return q.scalars().one_or_none()

    def select_shop_units(self, ids: List[UUID], depth: int) -> Select:
        return (self.select_all_shop_units(depth)
                .filter(ShopUnit.id.in_(ids)))  # type: ignore

    async def shop_units(self, db: DB, ids: List[UUID],
                         depth: int = 0) -> List[ShopUnit]:
        q = await db.execute(self.select_shop_units(ids, depth))
        return q.scalars().all()

    async def shop_unit_parent(self, db: DB, parent_id: UUID,
                               depth: int = 0) -> ShopUnit:
        q = await db.execute(self.select_shop_unit(parent_id, depth))
        return q.scalars().one()

    async def shop_units_parents(self, db: DB, parent_ids: Iterable[UUID],
                                 depth: int = 0) -> List[ShopUnit]:
        tasks = [self.shop_unit_parent(db, id, depth) for id in parent_ids]
        return await gather(*tasks)  # type: ignore

    async def all_shop_unit_parents(
        self, db: DB, parent_id: Optional[UUID],
        results: List[ShopUnit], ids: Set[UUID],
        depth: int = 0
    ) -> None:

        if parent_id is None:
            return None

        if parent_id in ids:
            return None
        ids.add(parent_id)

        it = await self.shop_unit_parent(db, parent_id, depth)
        results.append(it)
        await self.all_shop_unit_parents(db, it.parentId, results, ids, depth)

    async def all_shop_units_parents(
        self, db: DB, parent_ids: Iterable[Optional[UUID]], depth: int = 0
    ) -> Tuple[List[ShopUnit], Set[UUID]]:

        results: List[ShopUnit] = []
        ids: Set[UUID] = set()
        tasks = [self.all_shop_unit_parents(db, id, results, ids, depth)
                 for id in parent_ids]
        await gather(*tasks)
        return results, ids

    async def update_shop_units(
        self, db: DB, units: Iterable[ShopUnit]
    ) -> List[ShopUnit]:

        # useful? make_transient_to_detached
        tasks = [db.merge(unit) for unit in units]
        result = await gather(*tasks)
        await db.flush()
        return result  # type: ignore


crud = CRUD()
