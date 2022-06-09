from pathlib import Path

import yaml


openapi_yaml = Path(__file__).parent / "openapi.yaml"
openapi: dict = yaml.safe_load(openapi_yaml.read_text("utf-8"))

info: dict = openapi["info"]
paths: dict = openapi["paths"]
schemas: dict = openapi["components"]["schemas"]
