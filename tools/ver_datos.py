"""Muestra las paradas guardadas en Redis Cloud.

    python tools/ver_datos.py           # resumen legible
    python tools/ver_datos.py --json    # documentos JSON completos
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import probar_conexion, redis_client  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Lista las paradas en Redis Cloud")
    parser.add_argument("--json", action="store_true", help="imprime los JSON completos")
    args = parser.parse_args()

    if redis_client is None:
        print("REDIS_URL no está configurada. Revisa el archivo .env.")
        return 1

    if not probar_conexion():
        print("No se pudo conectar a Redis. Revisa credenciales o conexión.")
        return 1

    claves = sorted(redis_client.scan_iter(match="parada:*"))
    documentos = []
    for clave in claves:
        crudo = redis_client.get(clave)
        if crudo is None:
            continue
        documentos.append(json.loads(crudo))

    if args.json:
        print(json.dumps(documentos, ensure_ascii=False, indent=2))
        return 0

    print(f"Registros con prefijo 'parada:': {len(documentos)}")
    print(f"Claves totales en la base: {redis_client.dbsize()}")
    for parada in documentos:
        rutas = ", ".join(parada.get("rutas", [])) or "sin rutas"
        estado = "activa" if parada.get("activa") else "inactiva"
        print(
            f"- {parada.get('id')} | {parada.get('nombre')} "
            f"| {parada.get('colonia')} | {rutas} | {estado}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
