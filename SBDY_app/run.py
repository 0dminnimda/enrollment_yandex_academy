"""
This file allows you to run the app programmatically,
and also enables debugging if this file is run as the main
"""

import sys
from copy import deepcopy
from pathlib import Path

import uvicorn

from SBDY_app import options
from SBDY_app.app import app  # for uvicorn.run


DEBUGGING = "debugpy" in sys.modules


def run(host: str = "localhost") -> None:
    # from SBDY_app import options
    # print("run", __name__, options.DEV_MODE)

    file = Path(__file__)
    logfile = file.parent / "logfile.log"
    logfile.open(mode="a", encoding="utf-8").write("\n")

    config: dict = uvicorn.config.LOGGING_CONFIG  # type: ignore
    my_config: dict = deepcopy(config)

    default: dict = my_config["handlers"]["default"]
    default.pop("stream", None)
    default["filename"] = str(logfile)
    default["class"] = "logging.FileHandler"

    access: dict = my_config["handlers"]["access"]
    access.pop("stream", None)
    access["filename"] = str(logfile)
    access["class"] = "logging.FileHandler"

    uvicorn.run(
        f"{file.stem}:app",
        app_dir=str(file.parent.absolute()),
        host=host,
        port=80,
        reload=options.RELOAD,
        log_level="info",
        log_config=config if options.DEV_MODE else my_config,
        use_colors=options.DEV_MODE,
    )


if __name__ in ("__mp_main__", "__main__"):
    options.DEV_MODE = True
    # if this file is launched directly, this is a sign that it is a dev,
    # therefore, if we are not debugging, which requires RELOAD == False,
    # we set the RELOAD to True to simplify the development
    if not DEBUGGING:
        options.RELOAD = True

if __name__ == "__main__":
    run()
