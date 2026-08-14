# Pruebas de carga con Locust

Locust complementa los tests de `pytest`: simula usuarios concurrentes sobre un servidor HTTP real y reporta latencia, solicitudes por segundo y porcentaje de errores. No reemplaza las pruebas de validación, autorización o concurrencia ya existentes.

Es recomendable ejecutarlo antes de un despliegue o cuando necesites dimensionar la aplicación. Para desarrollo local sin usuarios concurrentes o para verificar reglas de negocio, no es necesario.

## Preparación

1. Usa una base de datos de pruebas. El escenario crea reservas y deja esos datos persistidos.
2. Crea un usuario regular con permisos de lectura y creación de reservas.
3. Crea un recurso y conserva su identificador.
4. Inicia la API:

```bash
uv run fastapi dev src/main.py
```

## Ejecución

Configura las credenciales y el recurso en `.env.locust`. Puedes partir de la plantilla:

```bash
cp .env.locust.example .env.locust
```

Completa los valores del archivo local. `locustfile.py` los carga automáticamente con `pydantic-settings`; no necesitas exportarlos en la terminal. `.env.locust` está ignorado por Git y `.env.locust.example` no contiene secretos.

Abre la interfaz de Locust:

```bash
uv run locust --host http://127.0.0.1:8000
```

En `http://127.0.0.1:8089`, inicia de forma gradual, por ejemplo, con 10 usuarios y 1 usuario por segundo. Revisa que el porcentaje de errores sea 0 y observa la latencia p95 de `GET /resources/`, `GET /reservations/` y `POST /reservations/`.

Para una ejecución no interactiva de 2 minutos:

```bash
uv run locust --host http://127.0.0.1:8000 --headless -u 10 -r 1 -t 2m
```

El escenario está definido en `locustfile.py`. Cada usuario inicia sesión mediante la cookie JWT del backend; las reservas creadas usan horarios futuros aleatorios para no generar conflictos deliberados.