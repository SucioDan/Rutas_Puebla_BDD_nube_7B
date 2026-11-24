"""Endpoints CRUD del recurso Paradas."""

from __future__ import annotations

import json

import redis
from fastapi import APIRouter, Depends, HTTPException, status

from app import database
from app.database import redis_client
from app.models import Parada

router = APIRouter(prefix="/paradas", tags=["Paradas"])


def get_redis() -> redis.Redis:
    """Dependencia que entrega el cliente de Redis o falla con un error claro."""
    cliente = database.redis_client
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis no está configurado: define REDIS_URL en el archivo .env",
        )
    return cliente


def _clave(parada_id: str) -> str:
    return f"parada:{parada_id}"


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_parada(parada: Parada, db: redis.Redis = Depends(get_redis)) -> dict:
    clave = _clave(parada.id)
    if db.exists(clave):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La parada ya existe",
        )

    db.set(clave, parada.model_dump_json())
    return {"mensaje": "Parada creada", "id": parada.id}


@router.get("")
@router.get("/", include_in_schema=False)
def listar_paradas(db: redis.Redis = Depends(get_redis)) -> dict:
    paradas: list[dict] = []

    for clave in db.scan_iter(match="parada:*"):
        datos = db.get(clave)
        if datos is None:
            continue
        paradas.append(json.loads(datos))

    paradas.sort(key=lambda p: (p.get("nombre", ""), p.get("id", "")))
    return {"total": len(paradas), "paradas": paradas}


@router.get("/{parada_id}")
def obtener_parada(parada_id: str, db: redis.Redis = Depends(get_redis)) -> dict:
    datos = db.get(_clave(parada_id))
    if not datos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parada no encontrada",
        )
    return json.loads(datos)


@router.put("/{parada_id}")
def actualizar_parada(
    parada_id: str,
    parada: Parada,
    db: redis.Redis = Depends(get_redis),
) -> dict:
    clave = _clave(parada_id)
    datos = db.get(clave)
    if not datos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parada no encontrada",
        )

    anterior = json.loads(datos)
    # El id de la ruta manda y se conserva la fecha original de creación.
    actualizada = Parada.model_validate(
        {
            **parada.model_dump(),
            "id": parada_id,
            "creado_en": anterior.get("creado_en", parada.creado_en),
        }
    )

    db.set(clave, actualizada.model_dump_json())
    return {"mensaje": "Parada actualizada", "parada": actualizada}


@router.delete("/{parada_id}")
def eliminar_parada(parada_id: str, db: redis.Redis = Depends(get_redis)) -> dict:
    clave = _clave(parada_id)
    if not db.exists(clave):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parada no encontrada",
        )

    db.delete(clave)
    return {"mensaje": "Parada eliminada", "id": parada_id}


__all__ = ["router", "redis_client", "get_redis", "crear_parada", "listar_paradas"]
