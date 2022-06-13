"""
This file allows you to run the app programmatically,
and also enables debugging if this file is run as the main
"""

import sys
from pathlib import Path

import uvicorn

from SBDY_app.app import app  # for uvicorn.run


RELOAD = False  # by default we don't reload, normal production mode
DEBUGGING = 'debugpy' in sys.modules


def run(host: str = "localhost") -> None:
    file = Path(__file__)
    uvicorn.run(
        f"{file.stem}:app",
        host=host,
        port=80,
        reload=RELOAD,
        log_level="info",
        app_dir=str(file.parent.absolute())
    )


if __name__ == "__main__":
    # but if this file is launched directly, this is a sign that it is a dev,
    # therefore, if we do not debugging, which requires RELOAD == False,
    # we set the RELOAD to True to simplify the development
    if not DEBUGGING:
        RELOAD = True

    run()
