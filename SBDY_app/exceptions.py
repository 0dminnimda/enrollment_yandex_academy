from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import Error


class ItemNotFound(Exception):
    pass


ValidationFailed = RequestValidationError([])


response_400 = JSONResponse(status_code=400, content=jsonable_encoder(
    Error(code=400, message="Validation Failed")))


response_404 = JSONResponse(status_code=404, content=jsonable_encoder(
    Error(code=404, message="Item not found")))


async def handler_400(request: Request, exc: Exception) -> Response:
    return response_400


async def handler_404(request: Request, exc: Exception) -> Response:
    return response_404


def add_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(RequestValidationError)(handler_400)
    app.exception_handler(ItemNotFound)(handler_404)
