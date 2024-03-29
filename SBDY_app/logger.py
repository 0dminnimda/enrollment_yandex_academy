from copy import deepcopy
from pathlib import Path

import uvicorn


LOGFILE = Path(__file__).parent / "logfile.log"

UVICORN_CONFIG: dict = uvicorn.config.LOGGING_CONFIG  # type: ignore
CONFIG: dict = deepcopy(UVICORN_CONFIG)

_default: dict = CONFIG["handlers"]["default"]
_default.pop("stream", None)
_default["filename"] = str(LOGFILE)
_default["class"] = "logging.FileHandler"

_access: dict = CONFIG["handlers"]["access"]
_access.pop("stream", None)
_access["filename"] = str(LOGFILE)
_access["class"] = "logging.FileHandler"


def setup(name: str):
    CONFIG["handlers"][name] = {
        "formatter": "default",
        "filename": str(LOGFILE),
        "class": "logging.FileHandler",
    }

    UVICORN_CONFIG["handlers"][name] = {
        "formatter": "default",
        "stream": "ext://sys.stdout",
        "class": "logging.StreamHandler",
    }

    CONFIG["loggers"][name] = UVICORN_CONFIG["loggers"][name] = {
        "handlers": [name], "level": "INFO"}
