import logging
from datetime import datetime
from typing import Any, Callable

from ciso8601 import parse_datetime, parse_rfc3339


def strict_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    try:
        # raises TypeError value is not a string
        # raises ValueError if string is invalid datetime
        return parse_datetime(value)  # parse_rfc3339(v)
    except Exception as e:
        from pydantic.errors import DateTimeError

        raise DateTimeError() from e


def patch_datetime_validation() -> None:
    from pydantic.validators import _VALIDATORS

    for i, (tp, _) in enumerate(_VALIDATORS):
        if tp == datetime:
            _VALIDATORS[i] = (tp, [strict_datetime])
            break


def serialize_datetime(dt: datetime) -> str:
    return dt.isoformat(timespec="milliseconds") + "Z"


def patch_datetime_serialization() -> None:
    from pydantic.json import ENCODERS_BY_TYPE

    ENCODERS_BY_TYPE[datetime] = serialize_datetime


def request_response(func: Callable):
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    from starlette import routing
    from starlette.concurrency import run_in_threadpool
    from starlette.requests import Request
    from starlette.types import ASGIApp, Receive, Scope, Send

    from . import __name__ as mod_name

    logger = logging.getLogger(mod_name)

    is_coroutine = routing.iscoroutinefunction_or_partial(func)

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive=receive, send=send)
        logger.info(f"{await request.body()!r}")
        if is_coroutine:
            response = await func(request)
        else:
            response = await run_in_threadpool(func, request)
        await response(scope, receive, send)

    return app


def patch_request_response() -> None:
    from starlette import routing
    routing.request_response = request_response


def patch() -> None:
    patch_datetime_validation()
    patch_datetime_serialization()
    patch_request_response()
