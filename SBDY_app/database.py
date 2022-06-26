import asyncio
from pathlib import Path
import time
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from . import options
from .models import Base
from .typedefs import DB


DATABASE_URL = f"sqlite+aiosqlite:///{Path(__file__).parent}/sqlite.db"

engine = create_async_engine(DATABASE_URL, future=True,
                             connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, class_=DB, expire_on_commit=False)


_READY_FOR_REQUEST = True


async def wait_db_to_finish(delta: float = 0.075, timeout: float = 1.) -> bool:
    """
    Wait till db will be available for the work.
    Returns `True` if the wait was timed out.
    """

    global _READY_FOR_REQUEST
    if _READY_FOR_REQUEST:
        return False

    max_time = time.time() + timeout
    while time.time() < max_time:
        if _READY_FOR_REQUEST:
            return False
        print("wait")
        await asyncio.sleep(delta)

    return True


async def get_db() -> AsyncGenerator[DB, None]:
    # if we will not wait the db will not be updated properly
    # which will lead to incorrect behavior
    await wait_db_to_finish()

    global _READY_FOR_REQUEST
    _READY_FOR_REQUEST = False

    async with SessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            _READY_FOR_REQUEST = True


db_injection = Depends(get_db)


async def db_startup() -> None:
    async with engine.begin() as conn:
        if options.DEV_MODE:
            await conn.run_sync(Base.metadata.drop_all)  # type: ignore
        await conn.run_sync(Base.metadata.create_all)  # type: ignore


async def db_shutdown() -> None:
    if options.DEV_MODE:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # type: ignore

    await engine.dispose()
