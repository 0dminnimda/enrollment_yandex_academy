import logging

from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import InvalidRequestError

from . import __name__ as mod_name
from .schemas import Error


logger = logging.getLogger(mod_name)


class ItemNotFound(Exception):
    pass


ValidationFailed = RequestValidationError([])


response_400 = JSONResponse(status_code=400, content=jsonable_encoder(
    Error(code=400, message="Validation Failed")))


response_404 = JSONResponse(status_code=404, content=jsonable_encoder(
    Error(code=404, message="Item not found")))


async def handler_400(request: Request, exc: Exception) -> Response:
    logger.error("Error handler: " + repr(request))
    logger.error("Error handler: " + repr(exc))
    return response_400


async def handler_404(request: Request, exc: Exception) -> Response:
    logger.error("Error handler: " + repr(request))
    logger.error("Error handler: " + repr(exc))
    return response_404


def add_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(RequestValidationError)(handler_400)
    app.exception_handler(ItemNotFound)(handler_404)


class NotEnoughResultsFound(InvalidRequestError):
    """
    A database result was required to be specific length but was not.
    """
