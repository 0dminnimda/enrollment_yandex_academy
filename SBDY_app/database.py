from pathlib import Path
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


async def get_db() -> AsyncGenerator[DB, None]:
    async with SessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


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
