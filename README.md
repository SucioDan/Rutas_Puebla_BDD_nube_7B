# Rutas Puebla — Sprint 1

API CRUD de paradas de transporte público de Puebla construida con **Python +
FastAPI + Redis Cloud**, con frontend web (HTML/CSS/JS) y mapa interactivo
(Leaflet + OpenStreetMap).

## Contenido del sprint

- CRUD completo de la entidad **Parada** (`POST`, `GET`, `GET/{id}`, `PUT/{id}`,
  `DELETE/{id}`).
- Persistencia como documentos **JSON** en Redis Cloud con claves `parada:{id}`.
- Conexión a Redis Cloud mediante `REDIS_URL` (`redis://` en el plan Free,
  `rediss://` si tu plan tiene TLS).
- Frontend responsive con formulario, listado, edición, eliminación y mensajes
  de éxito/error.
- Mapa de Puebla con un marcador por parada y botón **“Ver en mapa”**.
- Documentación automática (Swagger) en `/docs`.
- Pruebas automatizadas con `pytest` + `fakeredis` (no necesitan la nube).

## Estructura

```
rutas-puebla/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI, CORS, estáticos, / y /estado
│   ├── database.py    # conexión a Redis Cloud y PING
│   ├── models.py      # modelo Pydantic Parada
│   └── routes.py      # endpoints CRUD
├── static/
│   ├── index.html     # vista principal + Leaflet
│   ├── styles.css
│   └── app.js         # fetch(), CRUD y mapa
├── tests/
│   └── test_api.py
├── tools/
│   ├── ver_datos.py   # lista las paradas guardadas en Redis Cloud
│   └── demo_server.py # modo demo con Redis en memoria
├── .env               # REDIS_URL (no se sube al repo)
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

## Requisitos

- Python 3.11 o superior.
- Una base de datos en [Redis Cloud](https://redis.io/cloud/) (plan gratuito
  suficiente).

## 1. Instalación

```powershell
cd rutas-puebla
python -m venv venv
.\venv\Scripts\Activate.ps1        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configurar Redis Cloud

1. Entra a Redis Cloud → **Databases** → tu base → **Connect**.
2. Copia el *public endpoint*, el usuario (`default`) y la contraseña.
3. Crea el archivo `.env` (ya viene una plantilla) con la cadena completa:

```env
# Plan Free (sin TLS)
REDIS_URL=redis://default:TU_PASSWORD@TU_HOST:TU_PUERTO

# Plan de pago con TLS activado en Security
REDIS_URL=rediss://default:TU_PASSWORD@TU_HOST:TU_PUERTO
```

> **Importante:** TLS solo está disponible en planes de pago. En el plan Free el
> endpoint habla Redis sin cifrar, y usar `rediss://` da
> `[SSL: WRONG_VERSION_NUMBER]`. Si activas TLS en el panel, cambia a `rediss://`.
> El archivo `.env` está en `.gitignore`: nunca subas la contraseña.

Comprueba la conexión:

```powershell
python -c "from app.database import probar_conexion; print(probar_conexion())"
```

Debe imprimir `True`. También puedes abrir `/estado` con la app corriendo.

## 3. Ejecutar

```powershell
uvicorn app.main:app --reload
```

- Aplicación (frontend + mapa): <http://127.0.0.1:8000/>
- Documentación Swagger: <http://127.0.0.1:8000/docs>
- Estado de Redis: <http://127.0.0.1:8000/estado>

## 4. Endpoints

| Método | Ruta            | Acción                    | Éxito |
| ------ | --------------- | ------------------------- | ----- |
| POST   | `/paradas`      | Crear parada              | 201   |
| GET    | `/paradas`      | Listar paradas            | 200   |
| GET    | `/paradas/{id}` | Obtener una parada        | 200   |
| PUT    | `/paradas/{id}` | Actualizar una parada     | 200   |
| DELETE | `/paradas/{id}` | Eliminar una parada       | 200   |
| GET    | `/estado`       | Proyecto + estado de Redis | 200  |
| GET    | `/health`       | Liveness (200 si el proceso vive) | 200 |

Errores: `404` si la parada no existe, `409` si se intenta crear un ID
duplicado, `422` si los datos no son válidos y `503` si falta `REDIS_URL`.

### Modelo de datos

```json
{
  "id": "pue-001",
  "nombre": "Parada Zócalo",
  "colonia": "Centro",
  "municipio": "Puebla",
  "latitud": 19.0431,
  "longitud": -98.1937,
  "rutas": ["Ruta 1", "Ruta 15", "Ruta 72"],
  "activa": true,
  "creado_en": "2026-11-08T23:00:00Z"
}
```

Si no envías `id`, se genera uno con el formato `pue-xxxxxxxx`.

### Ejemplos con curl

```bash
# Crear
curl -X POST http://127.0.0.1:8000/paradas \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Parada BUAP","colonia":"Los Volcanes","latitud":19.0467,"longitud":-98.2065,"rutas":["Ruta 4","Ruta 61"],"activa":true}'

# Listar
curl http://127.0.0.1:8000/paradas

# Consultar
curl http://127.0.0.1:8000/paradas/pue-001

# Actualizar
curl -X PUT http://127.0.0.1:8000/paradas/pue-001 \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Parada Zócalo","colonia":"Centro","latitud":19.0431,"longitud":-98.1937,"rutas":["Ruta 1"],"activa":false}'

# Eliminar
curl -X DELETE http://127.0.0.1:8000/paradas/pue-001
```

## 5. Consultar los registros guardados

Tres formas, de la más rápida a la más visual:

```powershell
# 1) Resumen legible de las paradas
.\venv\Scripts\python.exe tools\ver_datos.py

# 2) Documentos JSON completos
.\venv\Scripts\python.exe tools\ver_datos.py --json
```

3. En la web: <http://127.0.0.1:8000/> (lista), <http://127.0.0.1:8000/docs>
   (`GET /paradas` → *Try it out*) o <http://127.0.0.1:8000/paradas> (JSON crudo).

En el panel de Redis Cloud también puedes verlo sin código:
**tu base → Connect → Launch Redis Insight web → Browse**, y busca las claves
con prefijo `parada:`.

## 6. Pruebas

```powershell
pip install -r requirements-dev.txt
pytest -v
```

Las pruebas usan `fakeredis`, así que puedes ejecutarlas sin credenciales y sin
tocar los datos reales de Redis Cloud.

Prueba manual de los cinco endpoints: abre `/docs`, usa **Try it out** en cada
operación y verifica que el listado del frontend se actualiza.

## Notas de implementación

- `decode_responses=True` hace que redis-py devuelva texto en lugar de `bytes`.
- El listado usa `SCAN` (`scan_iter`) en vez de `KEYS` para no bloquear Redis.
- En `PUT` el `id` de la URL siempre manda y se conserva `creado_en` original.
- El frontend escapa el contenido antes de insertarlo en el DOM.
- Al hacer clic en el mapa se rellenan latitud/longitud del formulario.

## Siguiente sprint

El modelo y las claves ya quedan preparados para agregar búsqueda por colonia,
geolocalización y consultas geoespaciales (Redis `GEO`/`FT.SEARCH`).
