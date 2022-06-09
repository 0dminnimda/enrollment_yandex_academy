from datetime import datetime
from typing import Any

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


def patch_datetime_validation():
    from pydantic.validators import _VALIDATORS

    for i, (tp, _) in enumerate(_VALIDATORS):
        if tp == datetime:
            _VALIDATORS[i] = (tp, [strict_datetime])
            break


def patch():
    patch_datetime_validation()
