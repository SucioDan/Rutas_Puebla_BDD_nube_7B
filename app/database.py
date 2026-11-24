"""Conexión a Redis Cloud.

La cadena de conexión se toma de la variable de entorno REDIS_URL, por ejemplo:

    redis://default:password@host:puerto      # plan Free (sin TLS)
    rediss://default:password@host:puerto     # plan de pago con TLS activado

Redis Cloud solo ofrece TLS en planes de pago. Si el panel de tu base no tiene
la opción de TLS activada, usa ``redis://``; con ``rediss://`` obtendrías
``[SSL: WRONG_VERSION_NUMBER]``.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import urlparse

import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "").strip()


def _crear_cliente(url: str) -> redis.Redis | None:
    """Crea el cliente validando la URL para no romper el arranque de la app."""
    if not url or "TU_" in url:
        logger.warning(
            "REDIS_URL no está configurada. Edita el archivo .env con los datos "
            "de tu base en Redis Cloud."
        )
        return None

    try:
        partes = urlparse(url)
        if partes.scheme not in {"redis", "rediss"}:
            raise ValueError(f"esquema no soportado: {partes.scheme!r}")
        _ = partes.port  # fuerza la validación del puerto
    except ValueError as error:
        logger.error("REDIS_URL inválida (%s). Revisa el archivo .env.", error)
        return None

    return redis.from_url(
        url,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        health_check_interval=30,
    )


redis_client: redis.Redis | None = _crear_cliente(REDIS_URL)


def probar_conexion() -> bool:
    """Devuelve True si Redis responde al PING."""
    if redis_client is None:
        return False
    try:
        return bool(redis_client.ping())
    except redis.RedisError:
        return False
