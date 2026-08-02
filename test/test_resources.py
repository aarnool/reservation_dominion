from httpx import AsyncClient

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

async def test_create_resource_conflict_exception(admin_client: AsyncClient):
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
    """Prueba la excepción al intentar crear un recurso sin permisos (solo tiene scopes resources:read)."""
    payload = {
        "name": "Recurso Ilegal",
        "description": "Intento de usuario normal",
        "capacity": 5
    }
    response = await user_client.post("/resources/", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permiso para realizar esta acción"

async def test_get_resources_success(user_client: AsyncClient, admin_client: AsyncClient):
    """Prueba obtener la lista de recursos (tanto para admin como para user normal)."""
    # 1. Crear un par de recursos con el admin
    await admin_client.post("/resources/", json={"name": "Recurso 1", "capacity": 10})
    await admin_client.post("/resources/", json={"name": "Recurso 2", "capacity": 5})
    
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
