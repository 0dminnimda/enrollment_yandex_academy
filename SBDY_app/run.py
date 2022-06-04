"""
This file allows you to run the app programmatically,
and also enables debugging if this file is run as the main
"""

from pathlib import Path

import uvicorn

from SBDY_app.app import app  # for uvicorn.run


DEBUG = False


def run(docker: bool = False):
    file = Path(__file__)
    uvicorn.run(
        f"{file.stem}:app",
        host="0.0.0.0" if docker else "localhost",
        port=80,
        reload=not DEBUG,
        log_level="info",
        app_dir=str(file.parent.absolute())
    )


if __name__ == "__main__":
    DEBUG = True
    run(docker=False)
