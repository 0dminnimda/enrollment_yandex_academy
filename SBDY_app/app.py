from pathlib import Path
from typing import Mapping

import yaml
from fastapi import FastAPI


openapi_yaml = Path(__file__).parent / "openapi.yaml"
openapi = yaml.safe_load(openapi_yaml.read_text("utf-8"))


app = FastAPI(**openapi["info"])


def path_docs(path: str) -> Mapping[str, str]:
    result, = openapi["paths"][path].values()
    result.pop("requestBody", None)
    result.pop("parameters", None)
    return result


@app.post("/imports", **path_docs("/imports"))
def imports():
    return "Not implemented yet"


@app.delete("/delete/{id}", **path_docs("/delete/{id}"))
def delete():
    return "Not implemented yet"


@app.get("/nodes/{id}", **path_docs("/nodes/{id}"))
def nodes():
    return "Not implemented yet"


@app.get("/sales", **path_docs("/sales"))
def sales():
    return "Not implemented yet"


@app.get("/node/{id}/statistic", **path_docs("/node/{id}/statistic"))
def node_statistic():
    return "Not implemented yet"
