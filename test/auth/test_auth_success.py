from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.domains.auth.models import User


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
        "password": "password123",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testadmin"
    assert data["email"] == "testadmin@example.com"


# Prueba el inicio de sesión exitoso.
async def test_login_success(client: AsyncClient, db_session: AsyncSession):

    passwoard_hash = get_password_hash("password123")
    db_session.add(
        User(
            username="loginsuccess",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password=passwoard_hash,  # Hash de "password123"
        )
    )
    await db_session.commit()

    response = await client.post(
        "/auth/login", data={"username": "loginsuccess", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Inicio de sesión exitoso"
    assert "auth_token" in response.cookies


# Prueba el cierre de sesión.
async def test_logout_success(client: AsyncClient):
    response = await client.post("/auth/logout")
    assert response.status_code == 204
