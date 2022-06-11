from datetime import datetime
from uuid import UUID

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError

from .docs import info, paths
from .schemas import (Error, ImpRequest, ShopUnit, ShopUnitType, StatResponse,
                     StatUnit)
from .typedefs import AnyCallable
from .exceptions import ItemNotFound, response_400, response_404


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


@app.exception_handler(RequestValidationError)
async def handler_400(request: Request, exc: Exception) -> Response:
    return response_400


@app.exception_handler(ItemNotFound)
async def handler_404(request: Request, exc: Exception) -> Response:
    return response_404


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest) -> str:
    return "Not implemented yet"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID) -> str:
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}", response_model=ShopUnit)
async def nodes(id: UUID) -> ShopUnit:
    return "Not implemented yet"


@path_with_docs(app.get, "/sales", response_model=StatResponse)
async def sales(date: datetime) -> StatResponse:
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic", response_model=StatResponse)
async def node_statistic(id: UUID,
                         dateStart: datetime = datetime.min,
                         dateEnd: datetime = datetime.max) -> StatResponse:
    return "Not implemented yet"
