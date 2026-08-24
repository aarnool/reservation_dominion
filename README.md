# 📅 Sistema Monolítico de Reservaciones (API REST)

Bienvenido al repositorio del **Sistema Monolítico de Reservaciones**, un servicio web de alto rendimiento construido con **FastAPI**, **SQLAlchemy (Async)**, **PostgreSQL** y **Pydantic**.

El proyecto adopta un diseño modular basado en dominios (**Domain-Driven Architecture**) y cuenta con autenticación JWT, gestión de roles/permisos, control de concurrencia en reservas, almacenamiento de avatares en Cloudflare R2, envío de correos con Resend, suite de pruebas automatizadas con **Pytest** y pruebas de carga con **Locust**.

---

## Tabla de Contenidos

- [Requisitos Previos y Herramientas a Descargar](#-requisitos-previos-y-herramientas-a-descargar)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Variables de Entorno](#-variables-de-entorno)
- [Migraciones de Base de Datos (Alembic)](#-migraciones-de-base-de-datos-alembic)
- [Ejecución de la API](#-ejecución-de-la-api)
- [Documentación de la API (Swagger / ReDoc)](#-documentación-de-la-api-swagger--redoc)
- [Pruebas Automatizadas y de Carga](#-pruebas-automatizadas-y-de-carga)

---

## Requisitos Previos y Herramientas a Descargar

Antes de comenzar, asegúrate de descargar e instalar las siguientes herramientas en tu sistema:

1. **Python (v3.12+ o v3.14)**:
   - Intérprete y entorno de ejecución del lenguaje Python.
   - 🔗 [Descargar Python](https://www.python.org/downloads/)

2. **uv (Administrador de Paquetes y Entornos Python)**:
   - Gestor de paquetes y entornos virtuales ultra rápido para Python.
   - **Instalación en Linux/macOS**:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - **Instalación mediante pip**:
     ```bash
     pip install uv
     ```
   - 🔗 [Documentación oficial de uv](https://docs.astral.sh/uv/)

3. **PostgreSQL**:
   - Sistema de gestión de bases de datos relacionales (RDBMS). Puedes instalarlo localmente, ejecutarlo vía Docker o utilizar un proveedor cloud (Supabase, Neon, Render, AWS RDS).
   - 🔗 [Descargar PostgreSQL](https://www.postgresql.org/download/)

4. **Git**:
   - Sistema de control de versiones necesario para clonar el repositorio.
   - 🔗 [Descargar Git](https://git-scm.com/downloads)

5. **Servicios Externos (Opcionales para producción/funcionalidades completas)**:
   - **Cloudflare R2 / AWS S3**: Servicio de almacenamiento de objetos para avatares e imágenes.
   - **Resend**: Servicio API para envío de correos electrónicos transaccionales y notificaciones.

---

## Estructura del Proyecto

El código fuente está estructurado por dominios de negocio:

```text
.
├── alembic/              # Migraciones de base de datos con Alembic
├── doc_draft/            # Borradores de documentación técnica
├── docs/                 # Documentación técnica adicional
├── load_tests/           # Pruebas de carga con Locust y guía explicativa
├── src/                  # Código fuente principal de la aplicación
│   ├── core/             # Funcionalidades centrales (seguridad, hashing, JWT)
│   ├── domains/          # Módulos organizados por dominio
│   │   ├── auth/         # Autenticación, registro, login y roles
│   │   ├── notifications/# Gestión de notificaciones por email
│   │   ├── reservations/ # Lógica de negocio de reservas y reglas de concurrencia
│   │   ├── resources/   # Gestión de recursos reservables (salas, equipos)
│   │   └── users/        # Gestión de usuarios y perfiles
│   ├── config.py         # Configuración de la aplicación (Pydantic Settings)
│   ├── database.py       # Configuración de la base de datos asíncrona (SQLAlchemy + asyncpg)
│   ├── dependencies.py   # Inyección de dependencias para FastAPI
│   ├── main.py           # Configuración principal de FastAPI y middlewares (CORS)
│   └── models.py         # Exportación centralizada de modelos ORM
├── test/                 # Suite de pruebas automatizadas organizadas con Pytest
├── .env.example          # Plantilla con variables de entorno
├── .env.locust.example   # Plantilla para configuración de pruebas de carga
├── locustfile.py         # Escenario de pruebas de carga con Locust
├── pyproject.toml        # Archivo de configuración del proyecto y dependencias
└── README.md             # Documentación principal del proyecto
```

---

## Diagramas y arquitectura del sistema

La siguiente documentación visual resume la propuesta de diseño del proyecto y ayuda a entender la estructura funcional del sistema.

### Arquitectura conceptual

![Arquitectura conceptual](doc_draft/general/tipo-arquitectura.png)

### Arquitectura por componentes

![Arquitectura por componentes](doc_draft/general/diagrama-arquitectura-componentes.excalidraw.svg)

### Casos de uso

![Casos de uso](doc_draft/general/diagrama-de-casos-uso.excalidraw.svg)

### Modelo entidad-relación

![Modelo entidad-relación](doc_draft/general/diagrama-entidad-relacion.excalidraw.svg)

### Diagrama de despliegue

![Diagrama de despliegue](doc_draft/general/diagrama-despliegue.excalidraw.svg)

### Flujo de autenticación

#### Login

![Flujo de login](doc_draft/auth/login/diagrama-flujo-login.excalidraw.svg)

#### Registro

![Flujo de registro](doc_draft/auth/register/diagrama-flujo-register.excalidraw.svg)

---

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd "4. RESERVACION MONOLITICA"
```

### 2. Sincronizar e Instalar Dependencias con `uv`

Ejecuta el siguiente comando en la raíz del proyecto para crear automáticamente el entorno virtual (`.venv`) e instalar todas las dependencias especificadas en `pyproject.toml` y `uv.lock`:

```bash
uv sync
```

---

## Variables de Entorno

Crea un archivo `.env` tomando como base la plantilla `.env.example`:

```bash
cp .env.example .env
```

Configura los parámetros según tu entorno local o de producción:

```env
# Conexión a Base de Datos PostgreSQL
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reservaciones_db

# Llave Secreta para la firma de Tokens JWT
SECRET_KEY=tu_llave_secreta_segura

# Servicio de Correo Electrónico (Resend) (No obligaroio colocar cualquier valor)
RESEND_API_KEY=re_123456789

# Configuración de Almacenamiento Cloudflare R2 / AWS S3 (Pedirle a mi persona si es que quieres realizar pequeñas pruebas con R2 o crea tu mismo tu propia cuenta)
R2_ACCOUNT_ID=tu_account_id
R2_ENDPOINT=https://tu_account_id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=tu_access_key_id
R2_SECRET_ACCESS_KEY=tu_secret_access_key
R2_PUBLIC_DOMAIN=https://tu_dominio_publico.com
R2_BUCKET_AVATAR=avatars
```

---

## Migraciones de Base de Datos (Alembic)

Antes de levantar el servidor, asegúrate de tener la base de datos PostgreSQL creada y aplica las migraciones estructurales:

```bash
# Aplicar todas las migraciones a la base de datos
uv run alembic upgrade head
```

Para generar una nueva migración tras cambiar los modelos de SQLAlchemy:

```bash
uv run alembic revision --autogenerate -m "descripcion_de_los_cambios"
```

---

## Ejecución de la API

Para iniciar el servidor de desarrollo de FastAPI con recarga automática:

```bash
uv run fastapi dev src/main.py
```

Por defecto, la API estará disponible en `http://127.0.0.1:8000`.

---

## Documentación de la API (Swagger / ReDoc)

FastAPI genera automáticamente documentación interactiva. Una vez iniciado el servidor, puedes acceder desde tu navegador:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Pruebas Automatizadas y de Carga

### Pruebas Unitarias e Integración (Pytest)

La suite de pruebas cubre flujos de autenticación, reservas, validación de datos, reglas de negocio y concurrencia.

```bash
# Ejecutar todas las pruebas
uv run pytest

# Ejecutar con detalles (-v)
uv run pytest -v

# Ejecutar pruebas de un módulo específico
uv run pytest test/reservations/
```

Para conocer en detalle la organización y convenciones de las pruebas, revisa la documentación en [test/README-TEST.md](file:///home/aarnoolxd/Proyecto%20para%20GitHub/4.%20RESERVACION%20MONOLITICA/test/README-TEST.md).

### Pruebas de Carga (Locust) (Aun no finalizada, la construccion se realizara al finalizar el proyecto)

Permite simular múltiples usuarios concurrentes realizando reservas y consultas HTTP para observar el rendimiento y como lo soporta el API:

1. Configura el archivo `.env.locust`:
   ```bash
   cp .env.locust.example .env.locust
   ```
2. Inicia la interfaz interactiva de Locust:
   ```bash
   uv run locust --host http://127.0.0.1:8000
   ```
3. Ve a `http://127.0.0.1:8089` e ingresa el número de usuarios para evaluar el rendimiento y latencia p95.

Para detalles adicionales de las pruebas de carga, consulta [load_tests/README.md](file:///home/aarnoolxd/Proyecto%20para%20GitHub/4.%20RESERVACION%20MONOLITICA/load_tests/README.md).
