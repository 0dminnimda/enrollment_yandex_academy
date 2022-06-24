__version__ = "0.0.0"
__name__ = "SBDY_app"


from .patches import patch

patch()  # order is important

from .app import app
from . import logger
from .run import run

logger.setup(__name__)
