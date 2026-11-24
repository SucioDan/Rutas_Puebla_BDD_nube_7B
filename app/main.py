"""Punto de entrada de la API "Rutas Puebla"."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import probar_conexion, redis_client
from app.routes import router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Rutas Puebla",
    description=(
        "CRUD de paradas de transporte público en Puebla con Redis Cloud"
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def inicio() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/estado", tags=["Estado"])
def estado() -> dict:
    return {
        "proyecto": "Rutas Puebla",
        "redis_configurado": redis_client is not None,
        "redis_conectado": probar_conexion(),
    }


@app.get("/health", tags=["Estado"])
def health() -> dict:
    """Liveness para monitores: responde 200 mientras el proceso esté vivo."""
    conectado = probar_conexion()
    return {
        "estado": "ok" if conectado else "degradado",
        "redis_conectado": conectado,
    }
