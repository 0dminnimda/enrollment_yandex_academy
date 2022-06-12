from datetime import datetime
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError

from .crud import crud
from .datebase import db_injection, db_shutdown, db_startup
from .docs import info, paths
from .exceptions import ItemNotFound, response_400, response_404
from .models import ShopUnit as DBShopUnit
from .schemas import Error, ImpRequest, ShopUnit, ShopUnitType, StatResponse
from .typedefs import DB, AnyCallable


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


@app.on_event("startup")
async def startup():
    await db_startup()


@app.on_event("shutdown")
async def shutdown():
    await db_shutdown()


@app.exception_handler(RequestValidationError)
async def handler_400(request: Request, exc: Exception) -> Response:
    return response_400


@app.exception_handler(ItemNotFound)
async def handler_404(request: Request, exc: Exception) -> Response:
    return response_404


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest, db: DB = db_injection) -> str:
    args = dict(date=req.updateDate, sub_offers_count=0)
    units = await crud.update_shop_units(
        db, (DBShopUnit(**args, **i.dict()) for i in req.items))

    for unit in units:
        if unit.parentId is None:
            continue

        parent = await crud.shop_unit_parent(db, unit.parentId, depth=1)
        if parent.type == ShopUnitType.OFFER:
            raise RequestValidationError([])

    return "Successful import"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID) -> str:
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}", response_model=ShopUnit)
async def nodes(id: UUID, db: DB = db_injection):
    unit = await crud.shop_unit_by_id(db, id)
    if unit is None:
        raise ItemNotFound
    return unit


@path_with_docs(app.get, "/sales", response_model=StatResponse)
async def sales(date: datetime) -> StatResponse:
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic", response_model=StatResponse)
async def node_statistic(id: UUID,
                         dateStart: datetime = datetime.min,
                         dateEnd: datetime = datetime.max) -> StatResponse:
    return "Not implemented yet"
