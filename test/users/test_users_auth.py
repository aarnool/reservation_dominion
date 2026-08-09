from httpx import AsyncClient


# Verifica que un usuario normal no pueda obtener la lista de usuarios (403 Forbidden)
async def test_user_cannot_get_all_users(user_client: AsyncClient):
    response = await user_client.get("/users/")
    assert response.status_code == 403


# Verifica que un usuario normal no pueda consultar otro usuario por ID (403 Forbidden)
async def test_user_cannot_get_user_by_id(user_client: AsyncClient):
    response = await user_client.get("/users/1")
    assert response.status_code == 403


# Verifica que un cliente no autenticado no pueda acceder al módulo de usuarios (401 Unauthorized)
async def test_unauthenticated_cannot_access_users(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == 401
