"""Modelos Pydantic del dominio: paradas de transporte público."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


def _nuevo_id() -> str:
    return f"pue-{uuid.uuid4().hex[:8]}"


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class Parada(BaseModel):
    """Documento JSON que se guarda en Redis bajo la clave ``parada:{id}``."""

    id: str = Field(default_factory=_nuevo_id)
    nombre: str = Field(min_length=1, max_length=120)
    colonia: str = Field(min_length=1, max_length=120)
    municipio: str = Field(default="Puebla", min_length=1, max_length=120)
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    rutas: List[str] = Field(default_factory=list)
    activa: bool = True
    creado_en: datetime = Field(default_factory=_ahora)
