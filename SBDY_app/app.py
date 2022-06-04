from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from fastapi import FastAPI

from .docs import openapi
from .models import ShopUnitImportRequest

app = FastAPI(**openapi["info"])


AnyCallable = Callable[..., Any]


def path_with_docs(decorator: AnyCallable, path: str) -> AnyCallable:
    docs = openapi["paths"][path][decorator.__name__]

    docs.pop("requestBody", None)
    docs.pop("parameters", None)

    return decorator(path, **docs)


@path_with_docs(app.post, "/imports")
def imports(req: ShopUnitImportRequest):
    return "Not implemented yet"


@path_with_docs(app.delete, "/delete/{id}")
def delete(id: UUID):
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}")
def nodes(id: UUID):
    return "Not implemented yet"


@path_with_docs(app.get, "/sales")
def sales(date: datetime):
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic")
def node_statistic(id: UUID):
    return "Not implemented yet"
