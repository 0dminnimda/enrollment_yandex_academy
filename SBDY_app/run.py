"""
This file allows you to run the app programmatically,
and also enables debugging if this file is run as the main
"""

import sys
from pathlib import Path

import uvicorn

from SBDY_app import options
from SBDY_app.app import app  # for uvicorn.run
from SBDY_app.logger import CONFIG, LOGFILE, UVICORN_CONFIG


DEBUGGING = "debugpy" in sys.modules


def run(host: str = "localhost") -> None:
    file = Path(__file__)
    LOGFILE.open(mode="a", encoding="utf-8").write("\n")

    uvicorn.run(
        f"{file.stem}:app",
        app_dir=str(file.parent.absolute()),
        host=host,
        port=80,
        reload=options.RELOAD,
        log_level="info",
        log_config=UVICORN_CONFIG if options.DEV_MODE else CONFIG,
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

# run without reloading but with stdout log
# py -3.10 -c "from SBDY_app import run, options;options.RELOAD = False;options.DEV_MODE = True;run('0.0.0.0')"  # noqa: E501
