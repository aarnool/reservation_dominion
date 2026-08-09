from httpx import AsyncClient


# Prueba obtener un usuario inexistente y espera 404 Not Found
async def test_get_user_by_id_not_found(admin_client: AsyncClient):
    response = await admin_client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario con ID 99999 no encontrado"
