import uvicorn
from pathlib import Path


docker = False


uvicorn.run(
    "__init__:app",
    host="0.0.0.0" if docker else "localhost",
    port=8080,
    reload=True,
    log_level="info",
    app_dir=str(Path(__file__).parent.absolute())
)
