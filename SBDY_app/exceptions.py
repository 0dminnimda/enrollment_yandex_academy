from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .schemas import Error


class ItemNotFound(Exception):
    pass


response_400 = JSONResponse(status_code=400, content=jsonable_encoder(
    Error(code=400, message="Validation Failed")))


response_404 = JSONResponse(status_code=404, content=jsonable_encoder(
    Error(code=404, message="Item not found")))
