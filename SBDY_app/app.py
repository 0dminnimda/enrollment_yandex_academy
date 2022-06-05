from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .docs import openapi
from .models import Error, ImpRequest


AnyCallable = Callable[..., Any]


def path_with_docs(decorator: AnyCallable, path: str) -> AnyCallable:
    docs = openapi["paths"][path][decorator.__name__]

    docs.pop("requestBody", None)
    docs.pop("parameters", None)

    for code, info in docs["responses"].items():
        if code == "400":
            info["model"] = Error
    docs["responses"]["422"] = {"description": "Never appears"}

    return decorator(path, **docs)


app = FastAPI(**openapi["info"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
    return JSONResponse(status_code=400, content=jsonable_encoder(
        Error(code=400, message="Validation Failed")))


@path_with_docs(app.post, "/imports")
async def imports(req: ImpRequest):
    return "Not implemented yet"


@path_with_docs(app.delete, "/delete/{id}")
async def delete(id: UUID):
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}")
async def nodes(id: UUID):
    return "Not implemented yet"


@path_with_docs(app.get, "/sales")
async def sales(date: datetime):
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic")
async def node_statistic(id: UUID):
    return "Not implemented yet"
