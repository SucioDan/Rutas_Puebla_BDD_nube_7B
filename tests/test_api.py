"""Pruebas del CRUD usando fakeredis (no requieren Redis Cloud)."""

from __future__ import annotations

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app import database, routes
from app.main import app


@pytest.fixture
def client(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(database, "redis_client", fake)
    monkeypatch.setattr(routes, "redis_client", fake)
    monkeypatch.setattr(routes.database, "redis_client", fake)

    with TestClient(app) as test_client:
        yield test_client

    fake.flushall()


PARADA = {
    "nombre": "Parada BUAP",
    "colonia": "Los Volcanes",
    "municipio": "Puebla",
    "latitud": 19.0467,
    "longitud": -98.2065,
    "rutas": ["Ruta 4", "Ruta 61"],
    "activa": True,
}


def test_crear_devuelve_id_unico(client):
    respuesta = client.post("/paradas", json=PARADA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["mensaje"] == "Parada creada"
    assert cuerpo["id"].startswith("pue-")


def test_ciclo_completo_crud(client):
    creada = client.post("/paradas", json=PARADA).json()
    parada_id = creada["id"]

    # Consultar por ID
    obtenida = client.get(f"/paradas/{parada_id}")
    assert obtenida.status_code == 200
    assert obtenida.json()["nombre"] == "Parada BUAP"

    # Listar
    listado = client.get("/paradas")
    assert listado.status_code == 200
    assert listado.json()["total"] == 1
    assert listado.json()["paradas"][0]["id"] == parada_id

    # Actualizar
    actualizada = client.put(
        f"/paradas/{parada_id}",
        json={**PARADA, "nombre": "Parada Zócalo", "activa": False},
    )
    assert actualizada.status_code == 200
    cuerpo = actualizada.json()["parada"]
    assert cuerpo["nombre"] == "Parada Zócalo"
    assert cuerpo["activa"] is False
    assert cuerpo["id"] == parada_id
    assert cuerpo["creado_en"] == obtenida.json()["creado_en"]

    # Eliminar
    eliminada = client.delete(f"/paradas/{parada_id}")
    assert eliminada.status_code == 200
    assert eliminada.json()["id"] == parada_id
    assert client.get(f"/paradas/{parada_id}").status_code == 404


def test_errores_claros(client):
    assert client.get("/paradas/pue-inexistente").status_code == 404
    assert (
        client.put("/paradas/pue-inexistente", json=PARADA).status_code == 404
    )
    assert client.delete("/paradas/pue-inexistente").status_code == 404

    creada = client.post("/paradas", json=PARADA).json()
    duplicada = client.post("/paradas", json={**PARADA, "id": creada["id"]})
    assert duplicada.status_code == 409
    assert duplicada.json()["detail"] == "La parada ya existe"


def test_validacion_de_coordenadas(client):
    invalida = {**PARADA, "latitud": 120}
    assert client.post("/paradas", json=invalida).status_code == 422


def test_lista_vacia(client):
    assert client.get("/paradas").json() == {"total": 0, "paradas": []}
