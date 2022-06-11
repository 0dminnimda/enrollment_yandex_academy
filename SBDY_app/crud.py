from asyncio import gather
from typing import Iterable, Optional
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
        await db.commit()

    def select_shop_units(self) -> Select:
        return select(ShopUnit).options(self.selection)


    def select_shop_unit_by_id(self, id: UUID) -> Select:
        return self.select_shop_units().filter(ShopUnit.id == id)

    async def shop_unit_by_id(self, db: DB, id: UUID) -> Optional[ShopUnit]:
        q = await db.execute(self.select_shop_unit_by_id(id))
        return q.scalars().one_or_none()

    async def update_units(self, db: DB, units: Iterable[ShopUnit]) -> None:
        tasks = [db.merge(unit) for unit in units]
        await gather(*tasks)
        await db.commit()


crud = CRUD()
