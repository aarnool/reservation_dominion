# Documentación de Tests

Esta carpeta contiene los tests automatizados del sistema de reservaciones.

Los tests se organizan por **módulo** y, dentro de cada módulo, por el **tipo de comportamiento** que se está verificando.

```text
test/
├── conftest.py
├── README-TEST.md
├── auth/
│   ├── test_auth_auth.py
│   ├── test_auth_concurrency.py
│   ├── test_auth_success.py
│   └── test_auth_validation.py
├── reservations/
│   ├── test_reservations_auth.py
│   ├── test_reservations_concurrency.py
│   ├── test_reservations_queries.py
│   ├── test_reservations_success.py
│   └── test_reservations_validation.py
└── resources/
    ├── test_resources_auth.py
    ├── test_resources_success.py
    └── test_resources_validation.py
```

## Organización por módulo

Cada carpeta contiene los tests de una funcionalidad concreta de la aplicación.

| Carpeta | Contenido |
|---|---|
| `auth/` | Tests relacionados con autenticación, credenciales, tokens y acceso de usuarios. |
| `reservations/` | Tests relacionados con la creación, consulta y reglas de las reservas. |
| `resources/` | Tests relacionados con los recursos que pueden reservarse. |
| `conftest.py` | Configuración y fixtures compartidas para toda la suite de tests. |

Por ejemplo, todos los tests de reservas se mantienen dentro de `test/reservations/`, independientemente de si prueban un caso exitoso, una validación o concurrencia.

---

## Tipos de tests

Los archivos siguen esta convención:

```text
test_<modulo>_<tipo>.py
```

Ejemplos:

```text
test_reservations_success.py
test_resources_validation.py
test_auth_concurrency.py
```

### `_auth`

Los tests terminados en `_auth.py` verifican que las rutas protegidas controlen correctamente quién puede acceder.

Incluyen casos como:

- Solicitud sin token.
- Token inválido o expirado.
- Usuario sin permisos suficientes.
- Usuario autenticado que sí puede acceder.

Estados esperados comunes:

- `401 Unauthorized`: el usuario no está autenticado.
- `403 Forbidden`: el usuario está autenticado, pero no tiene permisos.

Ejemplo actual:

```text
auth/test_auth_auth.py
```

Este archivo verifica que un usuario sin token no pueda acceder a un endpoint protegido.

---

### `_success`

Los tests terminados en `_success.py` verifican que los flujos correctos funcionen como se espera.

Incluyen casos como:

- Autenticación con datos válidos.
- Creación correcta de una reserva.
- Obtención correcta de un recurso.
- Respuesta correcta cuando los datos enviados son válidos.

Estados esperados comunes:

- `200 OK`
- `201 Created`
- `204 No Content`

Ejemplos actuales:

```text
auth/test_auth_success.py
reservations/test_reservations_success.py
resources/test_resources_success.py
```

---

### `_validation`

Los tests terminados en `_validation.py` verifican que el sistema aplique las validaciones definidas y rechace datos incorrectos.

Incluyen casos como:

- Campos obligatorios faltantes.
- Fechas inválidas.
- Formatos incorrectos.
- Valores fuera de los límites permitidos.
- Datos que incumplen una regla de negocio.

Estados esperados comunes:

- `400 Bad Request`
- `422 Unprocessable Entity`

Ejemplos actuales:

```text
auth/test_auth_validation.py
reservations/test_reservations_validation.py
resources/test_resources_validation.py
```

---

### `_concurrency`

Los tests terminados en `_concurrency.py` verifican qué ocurre cuando varias solicitudes se ejecutan al mismo tiempo.

Son necesarios cuando dos o más usuarios podrían intentar modificar, crear o acceder al mismo dato simultáneamente.

En el contexto de reservas, sirven para comprobar situaciones como:

- Dos usuarios intentando reservar el mismo recurso en el mismo horario.
- Varias solicitudes creando una reserva simultáneamente.
- Consistencia de los datos después de solicitudes concurrentes.
- Prevención de duplicados o condiciones de carrera.

Ejemplos actuales:

```text
auth/test_auth_concurrency.py
reservations/test_reservations_concurrency.py
```

No todos los módulos necesitan un archivo `_concurrency.py`. Solo debe existir si ese módulo tiene operaciones que puedan verse afectadas por solicitudes simultáneas.

---

### `_queries`

Los tests terminados en `_queries.py` verifican las operaciones de consulta de información.

Incluyen casos como:

- Listar reservas.
- Buscar una reserva.
- Filtrar resultados.
- Consultar un elemento específico.
- Validar respuestas vacías cuando no existen resultados.

Ejemplo actual:

```text
reservations/test_reservations_queries.py
```

---

## `conftest.py`

El archivo `test/conftest.py` contiene fixtures y configuraciones que pueden utilizar todos los tests.

Una fixture permite reutilizar elementos necesarios para ejecutar pruebas, por ejemplo:

- Cliente HTTP de prueba.
- Configuración de la aplicación.
- Usuarios de prueba.
- Tokens de autenticación.
- Datos iniciales requeridos por los tests.

Al estar en la raíz de la carpeta `test/`, las fixtures definidas allí están disponibles para los tests de `auth/`, `reservations/` y `resources/`.

Ejemplo de uso:

```python
async def test_example(client):
    response = await client.get("/resources/")
    assert response.status_code == 200
```

En este caso, `client` es una fixture definida en `conftest.py`.

---

## Dónde agregar un test nuevo

| Caso a probar | Archivo donde debe agregarse |
|---|---|
| Acceso a recursos sin token | `resources/test_resources_auth.py` |
| Crear un recurso con datos válidos | `resources/test_resources_success.py` |
| Crear un recurso con datos inválidos | `resources/test_resources_validation.py` |
| Acceso a reservas sin autenticación | `reservations/test_reservations_auth.py` |
| Crear una reserva válida | `reservations/test_reservations_success.py` |
| Crear una reserva con datos inválidos | `reservations/test_reservations_validation.py` |
| Consultar, filtrar o buscar reservas | `reservations/test_reservations_queries.py` |
| Dos solicitudes reservando simultáneamente | `reservations/test_reservations_concurrency.py` |
| Login o autenticación correcta | `auth/test_auth_success.py` |
| Credenciales o datos de autenticación inválidos | `auth/test_auth_validation.py` |

---

## Ejecución de los tests

Desde la raíz del proyecto:

```bash
# Ejecutar todos los tests
pytest

# Ejecutar todos los tests de reservas
pytest test/reservations/

# Ejecutar un archivo concreto
pytest test/reservations/test_reservations_validation.py

# Ejecutar con salida detallada
pytest -v
```

## Regla general

Antes de crear un test, se debe identificar:

1. El módulo al que pertenece: `auth`, `reservations` o `resources`.
2. El tipo de caso: `auth`, `success`, `validation`, `concurrency` o `queries`.

La ubicación final debe seguir este patrón:

```text
test/<modulo>/test_<modulo>_<tipo>.py
```