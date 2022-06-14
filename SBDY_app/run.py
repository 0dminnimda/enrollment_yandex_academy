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
    file = Path(__file__)

    config: dict = uvicorn.config.LOGGING_CONFIG  # type: ignore
    my_config: dict = deepcopy(config)
    default: dict = config["handlers"]["default"]
    del default["stream"]
    default["filename"] = str(file.parent / "logfile.log")
    default["class"] = "logging.FileHandler"

    uvicorn.run(
        f"{file.stem}:app",
        app_dir=str(file.parent.absolute()),
        host=host,
        port=80,
        reload=options.RELOAD,
        log_level="info",
        log_config=my_config if options.DEV_MODE else config,
        use_colors=options.DEV_MODE,
    )


if __name__ == "__main__":
    options.DEV_MODE = True

    # if this file is launched directly, this is a sign that it is a dev,
    # therefore, if we are not debugging, which requires RELOAD == False,
    # we set the RELOAD to True to simplify the development
    if not DEBUGGING:
        options.RELOAD = True

    run()
