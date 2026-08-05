from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.auth.models import User
from src.core.security import get_password_hash

# Verifica que un usuario no autenticado reciba 401 Unauthorized.
async def test_user_cannot_access_without_token(client: AsyncClient):
   
    response = await client.get("/resources/")
    assert response.status_code == 401



# Verifica que un usuario autenticado pueda acceder a una ruta protegida.
async def test_user_valid_session(user_client: AsyncClient):
    
    response = await user_client.get("/resources/")
    assert response.status_code == 200




# Prueba el registro exitoso de un nuevo usuario.
async def test_register_success(client: AsyncClient):
    user_data = {
        "username": "testadmin", 
        "email": "testadmin@example.com", 
        "first_name": "Test", 
        "last_name": "User", 
        "password": "password123"
    }
    response = await client.post(
        "/auth/register",
        json=user_data   
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testadmin"
    assert data["email"] == "testadmin@example.com"


# Prueba el conflico al registrar un usuario existente
async def test_register_conflict_exception(client: AsyncClient):
    user_data = {
        "username": "conflictuser", 
        "email": "conflict@example.com", 
        "first_name": "Test", 
        "last_name": "User", 
        "password": "password123"
    }
    await client.post("/auth/register", json=user_data) # Primera registro
    response = await client.post("/auth/register", json=user_data) # Intento de registro duplicado
    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre de usuario/correo ya está en uso"


# Prueba validación de correo inválido.
async def test_register_invalid_email(client: AsyncClient):
    user_data = {
        "username": "invalidemail", 
        "email": "notanemail", 
        "first_name": "Test", 
        "last_name": "User", 
        "password": "password123"
    }
    response = await client.post(
        "/auth/register",
        json=user_data
    )
    assert response.status_code == 422 # Lo maneja Pydantic, no FastAPI


# Prueba validación de contraseña corta.
async def test_register_short_password(client: AsyncClient):
    user_data = {
        "username": "shortpass", 
        "email": "shortpass@example.com",
        "first_name": "Test", 
        "last_name": "User", 
        "password": "short"
    }
    response = await client.post(
        "/auth/register",
        json=user_data
    )
    assert response.status_code == 422 # Lo maneja Pydantic, no FastAPI



# Prueba el inicio de sesión exitoso.
async def test_login_success(client: AsyncClient, db_session: AsyncSession):

    passwoard_hash = get_password_hash("password123")
    db_session.add(User(
        username="loginsuccess",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password=passwoard_hash  # Hash de "password123"
    ))
    await db_session.commit()
        
    response = await client.post(
        "/auth/login",
        data={
            "username": "loginsuccess", 
            "password": "password123"
        }
    
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Inicio de sesión exitoso"
    assert "auth_token" in response.cookies


# Prueba el inicio de sesión con usuario inexistente.
async def test_login_invalid_credentials_wrong_user(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={
            "username": "nonexistent", 
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


# Prueba el inicio de sesión con contraseña incorrecta.
async def test_login_invalid_credentials_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """Prueba el inicio de sesión con contraseña incorrecta."""
    passwoard_hash = get_password_hash("password123")
    db_session.add(User(
        username="loginsuccess",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password=passwoard_hash  # Hash de "password123"
    ))
    await db_session.commit()
    response = await client.post(
        "/auth/login",
        data={"username": "wrongpass", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"



# Prueba el cierre de sesión.
async def test_logout_success(client: AsyncClient):
    response = await client.post("/auth/logout")
    assert response.status_code == 204
