from fastapi import FastAPI


app_description = """
Вступительное задание в Летнюю Школу Бэкенд Разработки Яндекса 2022
"""


app = FastAPI(
    title="Mega Market Open API",
    description=app_description,
    version="1.0",
)


decs = {
    "imports": "",
    "delete": "",
    "nodes": "",
    "sales": "",
    "statistic": "",
}

tag1 = "Базовые задачи"
tag2 = "Дополнительные задачи"


@app.post("/imports", description=decs["imports"], tags=[tag1])
def imports():
    return "Not implemented yet"


@app.delete("/delete/{id}", description=decs["delete"], tags=[tag1])
def delete():
    return "Not implemented yet"


@app.get("/nodes/{id}", description=decs["nodes"], tags=[tag1])
def nodes():
    return "Not implemented yet"


@app.get("/sales", description=decs["sales"], tags=[tag2])
def sales():
    return "Not implemented yet"


@app.get("/node/{id}/statistic", description=decs["statistic"], tags=[tag2])
def node_statistic():
    return "Not implemented yet"
