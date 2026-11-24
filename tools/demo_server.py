"""Modo demo: levanta la API con un Redis en memoria (fakeredis).

Sirve para probar el CRUD y el frontend sin credenciales de Redis Cloud.
No se usa en producción.

    pip install -r requirements-dev.txt
    python tools/demo_server.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import fakeredis
import uvicorn

# Permite ejecutar el script desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import database

database.redis_client = fakeredis.FakeRedis(decode_responses=True)

from app.main import app  # noqa: E402  (después de inyectar el cliente falso)


if __name__ == "__main__":
    print("Modo demo con Redis en memoria en http://127.0.0.1:8010")
    uvicorn.run(app, host="127.0.0.1", port=8010)
