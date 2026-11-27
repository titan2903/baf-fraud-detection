"""Tulis openapi.json untuk di-import ke Postman. Jalankan: python -m scripts.export_openapi"""

import json
from pathlib import Path

from app.main import app

# hanya di file export: kalau dipasang di app, Swagger lokal default ke production dan kena CORS
SERVERS = [
    {"url": "https://fraudguard.yudista.tech", "description": "Production"},
    {"url": "http://localhost:8000", "description": "Lokal"},
]
OUT = Path(__file__).resolve().parent.parent / "openapi.json"


def build() -> dict:
    spec = dict(app.openapi())  # salinan: app.openapi() di-cache, jangan diubah
    return {"openapi": spec.pop("openapi"), "info": spec.pop("info"), "servers": SERVERS, **spec}


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"ditulis: {OUT}")
