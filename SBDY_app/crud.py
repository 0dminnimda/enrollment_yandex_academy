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

    def select_shop_units(self, depth: int) -> Select:
        if depth == 0:
            return select(ShopUnit)
        if depth < 0:
            return select(ShopUnit).options(self.selection)
        return select(ShopUnit).options(stack_selectinload(depth))

    def select_shop_unit(self, id: UUID, depth: int) -> Select:
        return self.select_shop_units(depth).filter(ShopUnit.id == id)

    async def shop_unit(self, db: DB, id: UUID,
                        depth: int = -1) -> Optional[ShopUnit]:
        q = await db.execute(self.select_shop_unit(id, depth))
        return q.scalars().one_or_none()

    async def update_shop_units(
        self, db: DB, units: Iterable[ShopUnit]
    ) -> Tuple[ShopUnit, ...]:

        tasks = [db.merge(unit) for unit in units]
        result = await gather(*tasks)
        await db.flush()
        return result


crud = CRUD()
