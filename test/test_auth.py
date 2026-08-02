from httpx import AsyncClient

async def test_register_success(client: AsyncClient):
    """Prueba el registro correcto de un usuario."""
    payload = {
        "username": "newuser",
        "email": "newuser@test.com",
        "first_name": "New",
        "last_name": "User",
        "password": "password123"
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"

async def test_register_conflict_exception(client: AsyncClient):
    """Prueba la excepción al intentar registrar un usuario que ya existe."""
    payload = {
        "username": "duplicateuser",
        "email": "duplicate@test.com",
        "first_name": "Duplicate",
        "last_name": "User",
        "password": "password123"
    }
    # Primer registro exitoso
    await client.post("/auth/register", json=payload)
    
    # Segundo registro falla por conflicto
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre de usuario/cooreo ya está en uso"

async def test_login_success(client: AsyncClient):
    """Prueba el inicio de sesión exitoso."""
    # Primero creamos el usuario
    payload_register = {
        "username": "loginuser",
        "email": "loginuser@test.com",
        "first_name": "Login",
        "last_name": "User",
        "password": "password123"
    }
    await client.post("/auth/register", json=payload_register)
    
    # Intentamos loguear (se pasa como formulario x-www-form-urlencoded)
    payload_login = {
        "username": "loginuser",
        "password": "password123"
    }
    response = await client.post("/auth/login", data=payload_login)
    assert response.status_code == 200
    assert response.json()["message"] == "Inicio de sesión exitoso"
    assert "auth_token" in response.cookies

async def test_login_unauthorized_user_not_found(client: AsyncClient):
    """Prueba la excepción al iniciar sesión con usuario inexistente."""
    payload_login = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", data=payload_login)
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuario no encontrado"


async def test_login_unauthorized_wrong_password(client: AsyncClient):
    """Prueba la excepción al iniciar sesión con contraseña incorrecta."""
    # Crear usuario primero
    payload_register = {
        "username": "wrongpassuser",
        "email": "wrongpass@test.com",
        "first_name": "Wrong",
        "last_name": "Pass",
        "password": "password123"
    }
    await client.post("/auth/register", json=payload_register)
    
    # Loguear con mala contraseña
    response = await client.post("/auth/login", data={"username": "wrongpassuser", "password": "wrong123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Contraseña incorrecta"


async def test_logout_success(client: AsyncClient):
    """Prueba el cierre de sesión exitoso."""
    response = await client.post("/auth/logout")
    assert response.status_code == 204
