from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import get_password_hash
from src.domains.auth.models import User


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
