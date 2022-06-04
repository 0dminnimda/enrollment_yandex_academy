from pathlib import Path
from typing import Any, Callable

import yaml
from fastapi import FastAPI


openapi_yaml = Path(__file__).parent / "openapi.yaml"
openapi = yaml.safe_load(openapi_yaml.read_text("utf-8"))


app = FastAPI(**openapi["info"])


AnyCallable = Callable[..., Any]


def path_with_docs(decorator: AnyCallable, path: str) -> AnyCallable:
    docs = openapi["paths"][path][decorator.__name__]

    docs.pop("requestBody", None)
    docs.pop("parameters", None)

    return decorator(path, **docs)


@path_with_docs(app.post, "/imports")
def imports():
    return "Not implemented yet"


@path_with_docs(app.delete, "/delete/{id}")
def delete():
    return "Not implemented yet"


@path_with_docs(app.get, "/nodes/{id}")
def nodes():
    return "Not implemented yet"


@path_with_docs(app.get, "/sales")
def sales():
    return "Not implemented yet"


@path_with_docs(app.get, "/node/{id}/statistic")
def node_statistic():
    return "Not implemented yet"
