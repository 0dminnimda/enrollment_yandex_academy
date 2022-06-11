from pathlib import Path
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from .crud import crud
from .models import Base
from .typedefs import DB


DATABASE_URL = f"sqlite+aiosqlite:///{Path(__file__).parent}/sqlite.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_async_engine(DATABASE_URL, future=True,
                             connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, class_=DB, expire_on_commit=False)


async def get_db() -> AsyncGenerator[DB, None]:
    async with SessionLocal() as session:
        async with session.begin():
            yield session


db_injection = Depends(get_db)


async def db_startup() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # type: ignore
        await conn.run_sync(Base.metadata.create_all)  # type: ignore

    async for db in get_db():
        await crud.startup(db)


async def db_shutdown() -> None:
    async for db in get_db():
        await crud.shutdown(db)

    await engine.dispose()

