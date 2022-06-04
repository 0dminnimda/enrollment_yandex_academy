from pathlib import Path

import yaml


openapi_yaml = Path(__file__).parent / "openapi.yaml"
openapi = yaml.safe_load(openapi_yaml.read_text("utf-8"))
