from httpx import AsyncClient


# Prueba el conflico al registrar un usuario existente
async def test_register_conflict_exception(client: AsyncClient):
    user_data = {
        "username": "conflictuser",
        "email": "conflict@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password123",
    }
    await client.post("/auth/register", data=user_data)  # Primera registro
    response = await client.post(
        "/auth/register", data=user_data
    )  # Intento de registro duplicado
    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre de usuario/correo ya está en uso"
