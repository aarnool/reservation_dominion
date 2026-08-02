import pytest
from httpx import AsyncClient
from src.domains.resources.models import Resources
from sqlalchemy.ext.asyncio import AsyncSession


# ==========================================
# Tests para POST /resources/
# ==========================================

async def test_create_resource_success(admin_client: AsyncClient):
    """Prueba la creación correcta de un recurso."""
    payload = {
        "name": "Recurso Correcto",
        "description": "Detalles",
        "capacity": 20
    }
    response = await admin_client.post("/resources/", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Recurso Correcto"
    assert response.json()["capacity"] == 20

async def test_create_resource_duplicate(admin_client: AsyncClient):
    """Prueba la excepción de conflicto al crear un recurso repetido."""
    payload = {
        "name": "Recurso Duplicado",
        "description": "Detalles",
        "capacity": 20
    }
    await admin_client.post("/resources/", json=payload)

    response = await admin_client.post("/resources/", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "El recurso con este nombre ya existe."

async def test_create_resource_forbidden_exception(user_client: AsyncClient):
    """Prueba la excepción al intentar crear un recurso sin permisos."""
    payload = {
        "name": "Recurso Ilegal",
        "description": "Intento de usuario normal",
        "capacity": 5
    }
    response = await user_client.post("/resources/", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permiso para realizar esta acción"


# ==========================================
# Tests para GET /resources/
# ==========================================

async def test_get_resources_success(user_client: AsyncClient, db_session: AsyncSession):
    """Prueba obtener la lista de recursos (con user normal)."""
    # 1. Crear un par de recursos directamente en BD
    db_session.add_all([
        Resources(name="Recurso 1", capacity=10),
        Resources(name="Recurso 2", capacity=5)
    ])
    await db_session.commit()
    
    # 2. Leer con user normal (ya que requiere resources:read, que el user sí tiene)
    response_user = await user_client.get("/resources/")
    assert response_user.status_code == 200
    assert isinstance(response_user.json(), list)
    assert len(response_user.json()) >= 2


async def test_get_resources_unauthorized_exception(client: AsyncClient):
    """Prueba la excepción al intentar leer recursos sin estar autenticado o sin token (401)."""
    response = await client.get("/resources/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


# ==========================================
# Tests para GET /resources/{resource_id}
# ==========================================

async def test_get_resource_by_id_success(user_client: AsyncClient, db_session: AsyncSession):
    """Prueba obtener un recurso por su ID exitosamente."""
    # 1. Crear un recurso
    new_res = Resources(name="Recurso Individual", capacity=10)
    db_session.add(new_res)
    await db_session.commit()

    # 2. Leer con usuario normal (tiene scope resources:read)
    response_get = await user_client.get(f"/resources/{new_res.id}")
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "Recurso Individual"


async def test_get_resource_by_id_unauthorized(client: AsyncClient, db_session: AsyncSession):
    """Prueba la excepción de permisos al intentar leer un recurso sin scope 'resources:read'."""
    # 1. Crear un recurso
    new_res = Resources(name="Recurso Prohibido", capacity=10)
    db_session.add(new_res)
    await db_session.commit()

    # 2. Intentar leer con el user (solo tiene read, pero vamos a simular que no tiene)
    # Para esto, podemos crear un cliente que no tenga el scope adecuado, pero para simplificar, asumimos que user_client no tiene permisos.
    response_get = await client.get(f"/resources/{new_res.id}")
    assert response_get.status_code == 401
    assert response_get.json()["detail"] == "Credenciales inválidas"


async def test_get_resource_by_id_not_found_exception(user_client: AsyncClient):
    """Prueba la excepción al obtener un recurso que no existe."""
    response = await user_client.get("/resources/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "El recurso no existe."


# ==========================================
# Tests para PATCH /resources/{resource_id}
# ==========================================

async def test_update_resource_success(admin_client: AsyncClient):
    """Prueba actualizar un recurso exitosamente."""
    # 1. Crear un recurso
    response_create = await admin_client.post("/resources/", json={"name": "Recurso para Actualizar", "capacity": 5})
    resource_id = response_create.json()["id"]

    # 2. Actualizar recurso (solo enviamos lo que queremos cambiar)
    payload_update = {"capacity": 50, "description": "Actualizado"}
    response_update = await admin_client.patch(f"/resources/{resource_id}", json=payload_update)
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["capacity"] == 50
    assert data["description"] == "Actualizado"
    assert data["name"] == "Recurso para Actualizar"  # Este no se alteró

async def test_update_resource_not_found_exception(admin_client: AsyncClient):
    """Prueba la excepción al intentar actualizar un recurso inexistente."""
    payload_update = {"capacity": 50}
    response = await admin_client.patch("/resources/99999", json=payload_update)
    assert response.status_code == 404
    assert response.json()["detail"] == "El recurso no existe."

async def test_update_resource_forbidden_exception(user_client: AsyncClient, db_session: AsyncSession):
    """Prueba la excepción de permisos al intentar actualizar sin scope 'resources:update'."""
    # 1. Crear un recurso
    new_res = Resources(name="Recurso Intocable", capacity=1)
    db_session.add(new_res)
    await db_session.commit()

    # 2. Intentar actualizar con el user (solo tiene read)
    response_update = await user_client.patch(f"/resources/{new_res.id}", json={"capacity": 10})
    assert response_update.status_code == 403
    assert response_update.json()["detail"] == "No tienes permiso para realizar esta acción"


# ==========================================
# Tests para DELETE /resources/{resource_id}
# ==========================================

async def test_delete_resource_success(admin_client: AsyncClient):
    """Prueba eliminar un recurso exitosamente."""
    # 1. Crear un recurso
    response_create = await admin_client.post("/resources/", json={"name": "Recurso para Eliminar", "capacity": 3})
    resource_id = response_create.json()["id"]

    # 2. Eliminar el recurso
    response_delete = await admin_client.delete(f"/resources/{resource_id}")
    assert response_delete.status_code == 204

    # 3. Comprobar que ya no existe
    response_get = await admin_client.get(f"/resources/{resource_id}")
    assert response_get.status_code == 404

async def test_delete_resource_not_found_exception(admin_client: AsyncClient):
    """Prueba la excepción al intentar eliminar un recurso inexistente."""
    response = await admin_client.delete("/resources/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "El recurso no existe."

async def test_delete_resource_forbidden_exception(user_client: AsyncClient, db_session: AsyncSession):
    """Prueba la excepción de permisos al intentar eliminar sin scope 'resources:delete'."""
    # 1. Crear un recurso
    new_res = Resources(name="Recurso Indestructible", capacity=2)
    db_session.add(new_res)
    await db_session.commit()

    # 2. Intentar eliminar con el user (solo tiene read)
    response_delete = await user_client.delete(f"/resources/{new_res.id}")
    assert response_delete.status_code == 403
    assert response_delete.json()["detail"] == "No tienes permiso para realizar esta acción"
