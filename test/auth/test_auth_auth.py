from httpx import AsyncClient


# Verifica que un usuario no autenticado reciba 401 Unauthorized al entrar a un endpoint protegido.
async def test_user_cannot_access_without_token(client: AsyncClient):

    response = await client.get("/resources/")
    assert response.status_code == 401
